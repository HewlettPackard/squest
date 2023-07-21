from django.db.models import CharField, ForeignKey, ManyToManyField, CASCADE

from Squest.utils.squest_model import SquestModel
from service_catalog.models import ApprovalStep


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
        verbose_name="Restricted scopes"
    )

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
        new_approval_workflow_state = ApprovalWorkflowState.objects.create(approval_workflow=self)
        for approval_step in self.approval_steps.all():
            new_app_workflow_state = ApprovalStepState.objects.create(approval_workflow_state=new_approval_workflow_state,
                                                                      approval_step=approval_step)
            if approval_step.position == 0:
                new_approval_workflow_state.current_step = new_app_workflow_state
        new_approval_workflow_state.save()
        return new_approval_workflow_state
