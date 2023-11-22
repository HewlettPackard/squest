from django.contrib.auth.models import User
from django.db.models import ForeignKey, CASCADE, SET_NULL, JSONField, DateTimeField, IntegerField, Q

from Squest.utils.squest_model import SquestModel
from service_catalog.models.approval_state import ApprovalState


class ApprovalStepState(SquestModel):

    class Meta:
        unique_together = ('approval_workflow_state', 'approval_step')
        ordering = ("approval_step__position",)

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
    state = IntegerField(
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

    def reset_to_pending(self):
        self.date_updated = None
        self.updated_by = None
        self.state = ApprovalState.PENDING
        self.save()

    def get_scopes(self):
        return self.approval_workflow_state.get_scopes()

    def who_can_approve(self):
        return self.approval_workflow_state.request.instance.quota_scope.who_has_perm(self.approval_step.permission.permission_str)

    @classmethod
    def get_q_filter(cls, user, perm):
        from service_catalog.models import Instance
        return Q(
            approval_workflow_state__request__instance__in=Instance.get_queryset_for_user(user, perm)
        )
