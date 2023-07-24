from datetime import datetime

from service_catalog.models import ApprovalWorkflow, ApprovalStep, ApprovalStepState, ApprovalWorkflowState, \
    ApprovalState
from tests.test_service_catalog.base import BaseTest


class TestApprovalStepState(BaseTest):

    def setUp(self):
        super(TestApprovalStepState, self).setUp()

        self.test_approval_workflow = ApprovalWorkflow.objects.create(name="test_approval_workflow",
                                                                      operation=self.create_operation_test)
        self.test_approval_workflow_state = ApprovalWorkflowState.objects.create(approval_workflow=self.test_approval_workflow)

        self.test_approval_step_1 = ApprovalStep.objects.create(name="test_approval_step_1",
                                                                approval_workflow=self.test_approval_workflow)

    def test_is_current_step_in_approval(self):
        test_approval_step_state_1 = ApprovalStepState.objects.create(approval_workflow_state=self.test_approval_workflow_state,
                                                                      approval_step=self.test_approval_step_1)
        self.test_approval_workflow_state.current_step = test_approval_step_state_1
        self.test_approval_workflow_state.save()
        self.assertTrue(test_approval_step_state_1.is_current_step_in_approval)

    def test_reset_to_pending(self):
        test_approval_step_state_1 = ApprovalStepState.objects.create(
            approval_workflow_state=self.test_approval_workflow_state,
            approval_step=self.test_approval_step_1,
            state=ApprovalState.APPROVED,
            updated_by=self.standard_user,
            date_updated=datetime.now())

        test_approval_step_state_1.reset_to_pending()
        self.assertIsNone(test_approval_step_state_1.date_updated)
        self.assertIsNone(test_approval_step_state_1.updated_by)
        self.assertEqual(test_approval_step_state_1.state, ApprovalState.PENDING)
