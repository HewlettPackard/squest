from django.contrib.auth.models import User
from django.db.models import ForeignKey, CASCADE, CharField, SET_NULL, JSONField, DateTimeField

from Squest.utils.squest_model import SquestModel
from service_catalog.models.approval_state import ApprovalState


class ApprovalStepState(SquestModel):

    class Meta:
        unique_together = ('approval_workflow_state', 'approval_step')

    approval_workflow_state = ForeignKey(
        "service_catalog.ApprovalWorkflowState",
        blank=False,
        null=False,
        on_delete=CASCADE,
        related_name='approval_step_states',
        related_query_name='approval_step_state'
    )

    approval_step = ForeignKey(
        "service_catalog.ApprovalStep",
        blank=False,
        null=False,
        on_delete=CASCADE,
        related_name='approval_step_states',
        related_query_name='approval_step_state'
    )
    state = CharField(
        max_length=10,
        choices=ApprovalState.choices,
        default=ApprovalState.PENDING,
        blank=False,
        null=False,
        verbose_name="Approval state"
    )
    updated_by = ForeignKey(
        User,
        null=True,
        on_delete=SET_NULL,
        related_name='approval_step_states',
        related_query_name='approval_step_state'
    )
    date_updated = DateTimeField(blank=True, null=True)
    fill_in_survey = JSONField(default=dict, blank=True)

    @property
    def is_current_step_in_approval(self):
        if self.approval_workflow_state.current_step == self:
            return True
        return False
