from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import ForeignKey, ManyToManyField, CharField, SET_NULL, QuerySet, CASCADE, IntegerField
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from profiles.models import RoleManager
from profiles.models.team import Team
from service_catalog.models import RequestState
from service_catalog.models.approval_step_type import ApprovalStepType
from django.utils.translation import ugettext_lazy as _

from service_catalog.models.approval_state import ApprovalState


class ApprovalStep(RoleManager):
    class Meta:
        unique_together = (('id', 'approval_workflow'), ('name', 'approval_workflow'))

    approval_workflow = ForeignKey(
        "service_catalog.ApprovalWorkflow",
        blank=False,
        null=False,
        on_delete=CASCADE,
        related_name="approval_step_list"
    )

    name = CharField(max_length=100, blank=False)

    teams = ManyToManyField(
        Team,
        related_name='approval_steps',
        related_query_name='approval_step'
    )
    type = CharField(
        max_length=12,
        choices=ApprovalStepType.choices,
        blank=False,
        null=False,
    )
    next = ForeignKey(
        "service_catalog.ApprovalStep",
        blank=True,
        null=True,
        default=None,
        on_delete=SET_NULL,
        related_name="previous"
    )

    position = IntegerField(null=True, blank=True)

    @property
    def is_entry_point(self):
        return self.approval_workflow.entry_point == self

    def __str__(self):
        return self.name

    def get_approvers(self):
        queryset = User.objects.none()
        for team in self.teams.all():
            queryset = QuerySet.union(queryset, team.get_all_users())
        return queryset

    def get_approvers_emails(self):
        return [user.email for user in self.get_approvers()]

    def _assert_no_loop(self):
        workflow_list = list()
        current = self
        while current:
            if current in workflow_list:
                raise ValidationError({'next': _("You cannot create a loop.")})
            workflow_list.append(current)
            current = current.next

    def _assert_no_duplicate_name_in_the_workflow(self):
        if ApprovalStep.objects.exclude(id=self.id).filter(approval_workflow=self.approval_workflow,
                                                           name=self.name).exists():
            raise ValidationError({'name': _("The name already exist in the workflow.")})

    def clean(self):
        self._assert_no_loop()
        self._assert_no_duplicate_name_in_the_workflow()

    def set_next(self, approval_step_id=None):
        self.next = ApprovalStep.objects.get(id=approval_step_id) if approval_step_id is not None else None
        self.save()

    def get_request_approval_state(self, request):
        """
        Check the status of the current step
        """
        approval_state_list = self.approval_step_states.filter(request=request)
        state_list = [approval_state.state for approval_state in approval_state_list]
        if ApprovalState.REJECTED in state_list:
            return ApprovalState.REJECTED
        elif self.type == ApprovalStepType.ALL_OF_THEM:
            if state_list.count(ApprovalState.APPROVED) == len(state_list):
                return ApprovalState.APPROVED
            else:
                return ApprovalState.PENDING
        elif self.type == ApprovalStepType.AT_LEAST_ONE:
            if ApprovalState.APPROVED in state_list:
                return ApprovalState.APPROVED
            else:
                return ApprovalState.PENDING

    def delete(self, using=None, keep_parents=False):
        # For all request linked to this approval step relink to the next one
        for request in self.requests.filter(state=RequestState.SUBMITTED):
            request.approval_step = self.next
            request.save()
        # When the approval step is the entry point set the next one as new one
        if self.approval_workflow.entry_point == self:
            self.approval_workflow.entry_point = self.next
            self.approval_workflow.save()
        # When none entry point is defined in the workflow remove this approval workflow from all operations and all
        # requests come from this operation
        if not self.approval_workflow.entry_point:
            for operation in self.approval_workflow.operation.all():
                operation.approval_workflow = None
                operation.save()
                for request in operation.request_set.filter(state=RequestState.SUBMITTED):
                    request.approval_step = None
                    request.save()
        # When a step is before its next is changed for the next of the current step
        previous = self.previous.first()
        if previous:
            previous.set_next(self.next.id if self.next else None)
        super(ApprovalStep, self).delete(using, keep_parents)
        self.approval_workflow.update_positions()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(ApprovalStep, self).save(force_insert, force_update, using, update_fields)
        self.approval_workflow.update_positions()


@receiver(post_save, sender=ApprovalStep)
def set_approver_role_and_entrypoint_approval_workflow(sender, instance, created, **kwargs):
    """
    Add the Approver role and change the entry point of the approval workflow when needed
    """
    if created:
        for team in instance.teams.all():
            instance.add_team_in_role(team, "Approver")
        if not instance.approval_workflow.entry_point or instance.next == instance.approval_workflow.entry_point:
            instance.approval_workflow.entry_point = instance
            instance.approval_workflow.save()


def teams_changed(sender, instance, **kwargs):
    current_teams = instance.get_teams_in_role("Approver")
    to_remove = list(set(current_teams) - set(instance.teams.all()))
    to_add = list(set(instance.teams.all()) - set(current_teams))
    for team in to_add:
        instance.add_team_in_role(team, "Approver")
    for team in to_remove:
        instance.remove_team_in_role(team, "Approver")


m2m_changed.connect(teams_changed, sender=ApprovalStep.teams.through)
