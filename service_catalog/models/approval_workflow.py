from django.db.models import CharField, ForeignKey, ManyToManyField, CASCADE, BooleanField
from hashlib import sha256
from Squest.utils.squest_model import SquestModel
from profiles.models import AbstractScope, GlobalScope, Scope
from service_catalog.models import TowerSurveyField, ApprovalStep, RequestState, Request


class ApprovalWorkflow(SquestModel):
    name = CharField(max_length=100, blank=False, unique=True)

    operation = ForeignKey(
        'service_catalog.Operation',
        related_name='approval_workflows',
        related_query_name='approval_workflow',
        blank=False,
        null=False,
        on_delete=CASCADE
    )

    scopes = ManyToManyField(
        'profiles.Scope',
        related_name='approval_workflows',
        blank=True,
        verbose_name="Restricted scopes",
        help_text="This workflow will be triggered for the following scopes. Leave empty to trigger for all scopes"
    )

    @property
    def get_unused_fields(self):
        all_fields = set(TowerSurveyField.objects.filter(operation=self.operation).values_list('name', flat=True))
        used_fields = set(
            TowerSurveyField.objects.filter(approval_steps_as_write_field__approval_workflow=self).values_list('name',
                                                                                                               flat=True))
        return all_fields - used_fields

    @property
    def hash(self):
        string = f"{self.enabled}_"
        for step in self.approval_steps.all().order_by('id'):
            string += f"{step.hash}_"
        return int(sha256(string.encode("utf-8")).hexdigest(),16) % 2 ** 31


    @property
    def first_step(self):
        first_step = ApprovalStep.objects.filter(approval_workflow=self, position=0)
        if first_step.exists():
            return first_step.first()
        return None

    def __str__(self):
        return self.name

    def instantiate(self):
        from service_catalog.models import ApprovalStepState
        from service_catalog.models import ApprovalWorkflowState
        new_approval_workflow_state = ApprovalWorkflowState.objects.create(approval_workflow=self, hash=self.hash)
        for approval_step in self.approval_steps.all():
            current_step_state = ApprovalStepState.objects.create(
                approval_workflow_state=new_approval_workflow_state,
                approval_step=approval_step)
            if approval_step.position == 0:
                new_approval_workflow_state.current_step = current_step_state
        new_approval_workflow_state.save()
        return new_approval_workflow_state

    def _get_all_requests_that_should_use_workflow(self):
        if not self.enabled:
            return Scope.objects.none()
        scopes_already_assigned_to_another_workflow = Scope.objects.filter(
            approval_workflows__operation=self.operation,
            approval_workflows__enabled=True
        ).exclude(
            approval_workflows__id=self.id
        )
        expanded_scopes = self.scopes.expand().exclude(id__in=scopes_already_assigned_to_another_workflow.values("id"))

        if self.scopes.exists():
            return Request.objects.filter(
                operation=self.operation,
                instance__quota_scope__id__in=expanded_scopes,
                state=RequestState.SUBMITTED
            )
        else:
            return Request.objects.filter(
                operation=self.operation,
                state=RequestState.SUBMITTED
            ).exclude(
                instance__quota_scope__id__in=scopes_already_assigned_to_another_workflow.expand()
            )

    def _get_request_using_workflow(self):
        return Request.objects.filter(approval_workflow_state__approval_workflow=self, state=RequestState.SUBMITTED)

    def _get_request_using_workflow_with_wrong_version(self):
        return self._get_request_using_workflow().exclude(approval_workflow_state__hash=self.hash)

    def _get_request_using_workflow_with_good_version(self):
        return self._get_request_using_workflow().filter(approval_workflow_state__hash=self.hash)

    def _get_request_to_reset(self):  # TODO Add tests
        return self._get_all_requests_that_should_use_workflow() \
            .exclude(id__in=self._get_request_using_workflow_with_good_version().values_list("id", flat=True)) \
            | self._get_request_using_workflow_with_wrong_version() \
            | self._get_request_using_workflow() \
                .exclude(id__in=self._get_all_requests_that_should_use_workflow().values_list("id", flat=True))

    def reset_all_approval_workflow_state(self):
        for request in self._get_request_to_reset().distinct():
            request.setup_approval_workflow()

    def get_scopes(self):
        scopes = AbstractScope.objects.none()
        for scope in self.scopes.all():
            scopes = scopes | scope.get_scopes()
        scopes = scopes.distinct()
        if scopes.exists():
            return scopes
        else:
            return GlobalScope.load().get_scopes()
