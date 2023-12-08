from service_catalog.models import ApprovalStepState, RequestState, ApprovalState
from tests.test_service_catalog.base_test_approval import BaseTestApproval


class TestApprovalWorkflowState(BaseTestApproval):

    def setUp(self):
        super(TestApprovalWorkflowState, self).setUp()

    def test_get_next_step(self):
        all_approval_step_states = ApprovalStepState.objects.filter(approval_workflow_state=self.test_approval_workflow_state)
        self.assertEqual(self.test_approval_workflow_state.current_step,
                         all_approval_step_states.filter(approval_step__position=0).first())
        self.assertEqual(self.test_approval_workflow_state.get_next_step(),
                         all_approval_step_states.filter(approval_step__position=1).first())
        self.test_approval_workflow_state.current_step = all_approval_step_states.filter(approval_step__position=1).first()
        self.test_approval_workflow_state.save()
        self.assertIsNone(self.test_approval_workflow_state.get_next_step())

    def test_approve_current_step(self):
        all_approval_step_states = ApprovalStepState.objects.filter(
            approval_workflow_state=self.test_approval_workflow_state)
        self.assertEqual(self.test_approval_workflow_state.current_step,
                         all_approval_step_states.filter(approval_step__position=0).first())
        self.test_approval_workflow_state.approve_current_step(user=self.standard_user, fill_in_survey={})
        self.test_approval_workflow_state.refresh_from_db()
        self.assertEqual(self.test_approval_workflow_state.current_step,
                         all_approval_step_states.filter(approval_step__position=1).first())
        self.assertEqual(self.test_request.state, RequestState.SUBMITTED)

        self.test_approval_workflow_state.approve_current_step(user=self.standard_user, fill_in_survey={})
        self.test_approval_workflow_state.refresh_from_db()
        self.assertIsNone(self.test_approval_workflow_state.current_step)
        self.test_request.refresh_from_db()
        self.assertEqual(self.test_request.state, RequestState.ACCEPTED)

    def test_reject_current_step(self):
        self.test_approval_workflow_state.reject_current_step(user=self.standard_user)
        self.test_approval_workflow_state.refresh_from_db()
        self.assertEqual(self.test_approval_workflow_state.current_step.state, ApprovalState.REJECTED)

    def test_reset(self):
        step1 = self.test_approval_workflow_state.approval_step_states.get(approval_step__position=0)
        step1.state = ApprovalState.APPROVED
        step1.save()
        step2 = self.test_approval_workflow_state.approval_step_states.get(approval_step__position=1)
        self.test_approval_workflow_state.current_step = step2
        self.test_approval_workflow_state.save()

        # reset
        self.test_approval_workflow_state.request.setup_approval_workflow()
        self.test_approval_workflow_state = self.test_request.approval_workflow_state
        self.assertEqual(self.test_approval_workflow_state.current_step.approval_step.position, 0)
        for step in self.test_approval_workflow_state.approval_step_states.all():
            self.assertEqual(step.state, ApprovalState.PENDING)
