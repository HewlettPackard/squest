from django.contrib.auth.models import User
from django.db.models import Model, ForeignKey, CASCADE, CharField, SET_NULL
from service_catalog.models.approval_state import ApprovalState


class ApprovalStepState(Model):
    class Meta:
        unique_together = ('request', 'approval_step', 'team')

    request = ForeignKey(
        "service_catalog.Request",
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
    team = ForeignKey(
        "profiles.Team",
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

    def set_state(self, user, state):
        self.state = state
        self.updated_by = user
        self.save()
