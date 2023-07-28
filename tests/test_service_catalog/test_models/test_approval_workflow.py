from service_catalog.models import ApprovalWorkflow, ApprovalStepState, ApprovalStep
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestApprovalWorkflow(BaseTestRequest):

    def setUp(self):
        super(TestApprovalWorkflow, self).setUp()

        self.test_approval_workflow = ApprovalWorkflow.objects.create(name="test_approval_workflow",
                                                                      operation=self.create_operation_test)

        self.test_approval_step_1 = ApprovalStep.objects.create(name="test_approval_step_1",
                                                                approval_workflow=self.test_approval_workflow)
        self.test_approval_step_2 = ApprovalStep.objects.create(name="test_approval_step_2",
                                                                approval_workflow=self.test_approval_workflow)

        self.test_approval_workflow_no_steps = ApprovalWorkflow.objects.create(name="test_approval_workflow_no_steps",
                                                                               operation=self.create_operation_test)

    def test_first_step(self):
        self.assertEqual(self.test_approval_workflow.first_step, self.test_approval_step_1)
        self.assertIsNone(self.test_approval_workflow_no_steps.first_step)

    def test_instantiate(self):
        number_step_state_before = ApprovalStepState.objects.all().count()
        new_approval_workflow_state = self.test_approval_workflow.instantiate()
        self.assertEqual(number_step_state_before + 2, ApprovalStepState.objects.all().count())

        created_steps = ApprovalStepState.objects.filter(
            approval_workflow_state__approval_workflow=self.test_approval_workflow).order_by('approval_step__position')
        first_step = created_steps.first()
        self.assertEqual(new_approval_workflow_state.current_step, first_step)
