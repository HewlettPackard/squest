from profiles.models.squest_permission import Permission

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
        test_approval_step_2.refresh_from_db()
        self.assertEqual(test_approval_step_2.position, 1)

    def test_default_perm_added_on_save(self):
        test_approval_step_1 = ApprovalStep.objects.create(name="test_approval_step_1",
                                                           approval_workflow=self.test_approval_workflow)
        self.assertIsNotNone(test_approval_step_1.permission)
        self.assertEqual(test_approval_step_1.permission, Permission.objects.get(codename="approve_reject_approvalstep"))
