from service_catalog.models import ApprovalWorkflow, ApprovalStep
from tests.test_service_catalog.base import BaseTest


class TestApprovalStep(BaseTest):

    def setUp(self):
        super(TestApprovalStep, self).setUp()

        self.test_approval_workflow = ApprovalWorkflow.objects.create(name="test_approval_workflow",
                                                                      operation=self.create_operation_test)

    def test_set_position(self):
        test_approval_step_1 = ApprovalStep.objects.create(name="test_approval_step_1",
                                                           approval_workflow=self.test_approval_workflow)
        self.assertEqual(test_approval_step_1.position, 0)

        test_approval_step_2 = ApprovalStep.objects.create(name="test_approval_step_2",
                                                           approval_workflow=self.test_approval_workflow)
        self.assertEqual(test_approval_step_2.position, 1)
