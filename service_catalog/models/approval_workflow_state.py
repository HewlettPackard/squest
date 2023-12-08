from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import ForeignKey, CASCADE, PositiveIntegerField

from Squest.utils.squest_model import SquestModel
from service_catalog.models import ApprovalState


class ApprovalWorkflowState(SquestModel):
    approval_workflow = ForeignKey(
        "service_catalog.ApprovalWorkflow",
        blank=False,
        null=False,
        on_delete=CASCADE,
        related_name='approval_workflow_states',
        related_query_name='approval_workflow_state'
    )

    current_step = ForeignKey(
        "service_catalog.ApprovalStepState",
        blank=True,
        null=True,
        on_delete=CASCADE,
        related_name='current_approval_workflow_states',
        related_query_name='current_approval_workflow_state'
    )

    hash = PositiveIntegerField(help_text="ApprovalWorkflow hash when instantiated", default=1)

    def get_scopes(self):
        return self.request.get_scopes()

    def get_next_step(self):
        next_step = self.approval_step_states.filter(approval_step__position=self.current_step.approval_step.position + 1)
        if next_step.exists():
            return next_step.first()
        return None

    def approve_current_step(self, user=None, fill_in_survey={}):
        self.current_step.fill_in_survey = fill_in_survey
        self.current_step.state = ApprovalState.APPROVED
        self.current_step.date_updated = datetime.now()
        self.current_step.updated_by = user
        self.current_step.save()
        self.current_step = self.get_next_step()
        self.save()
        if self.current_step is None:
            self.request.accept(user)

    def reject_current_step(self, user):
        self.current_step.state = ApprovalState.REJECTED
        self.current_step.date_updated = datetime.now()
        self.current_step.updated_by = user
        self.current_step.save()

    @property
    def first_step(self):
        first_step = self.approval_step_states.filter(approval_step__position=0)
        if first_step.exists():
            return first_step.first()
        return None

    def who_can_approve(self):
        if self.current_step is not None:
            return self.current_step.who_can_approve()
        return User.objects.none()
