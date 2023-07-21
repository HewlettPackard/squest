from datetime import datetime

from django.db.models import ForeignKey, CASCADE

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

    def move_to_next_step(self):
        next_step = self.approval_step_states.filter(approval_step__position=self.current_step.approval_step.position + 1)
        if next_step.exists():
            return next_step.first()
        return None

    def approve_current_step(self, user, fill_in_survey):
        self.current_step.fill_in_survey = fill_in_survey
        self.current_step.state = ApprovalState.APPROVED
        self.current_step.date_updated = datetime.now()
        self.current_step.updated_by = user
        self.current_step.save()
        self.current_step = self.move_to_next_step()
        self.save()
        if self.current_step is None:
            self.request.accept(user)

    def reject_current_step(self, user):
        self.current_step.state = ApprovalState.REJECTED
        self.current_step.date_updated = datetime.now()
        self.current_step.updated_by = user
        self.current_step.save()

    def reset_current_step_to_pending(self):
        self.current_step.state = ApprovalState.PENDING
        self.current_step.date_updated = None
        self.current_step.updated_by = None
        self.current_step.save()

    def reset_all_steps(self):
        for step in self.approval_step_states.all():
            step.date_updated = None
            step.updated_by = None
            step.state = ApprovalState.PENDING
            step.save()
        # place back the current step of the workflow on the first step of the workflow
        first_step = self.approval_step_states.filter(approval_step__position=0)
        if first_step.exists():
            self.current_step = first_step.first()
            self.save()
