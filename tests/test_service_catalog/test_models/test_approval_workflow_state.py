from service_catalog.models import ApprovalWorkflow, ApprovalStep, ApprovalStepState, RequestState, ApprovalState
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestApprovalWorkflowState(BaseTestRequest):

    def setUp(self):
        super(TestApprovalWorkflowState, self).setUp()

        self.test_approval_workflow = ApprovalWorkflow.objects.create(name="test_approval_workflow",
                                                                      operation=self.create_operation_test)
        self.test_approval_step_1 = ApprovalStep.objects.create(name="test_approval_step_1",
                                                                approval_workflow=self.test_approval_workflow)
        self.test_approval_step_2 = ApprovalStep.objects.create(name="test_approval_step_2",
                                                                approval_workflow=self.test_approval_workflow)
        self.test_approval_workflow_state = self.test_approval_workflow.instantiate()
        self.test_request.approval_workflow_state = self.test_approval_workflow_state
        self.test_request.save()

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
        step1 = self.test_approval_workflow_state.approval_step_states.filter(approval_step__position=0).first()
        step1.state = ApprovalState.APPROVED
        step1.save()
        step2 = self.test_approval_workflow_state.approval_step_states.filter(approval_step__position=1).first()
        self.test_approval_workflow_state.current_step = step2
        self.test_approval_workflow_state.save()

        # reset
        self.test_approval_workflow_state.reset()
        self.test_approval_workflow_state.refresh_from_db()
        self.assertEqual(self.test_approval_workflow_state.current_step, step1)
        for step in self.test_approval_workflow_state.approval_step_states.all():
            self.assertEqual(step.state, ApprovalState.PENDING)
