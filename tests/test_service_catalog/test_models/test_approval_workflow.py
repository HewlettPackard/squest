from tests.test_service_catalog.base_approval import BaseApproval


class TestApprovalWorkflow(BaseApproval):

    def setUp(self):
        super(TestApprovalWorkflow, self).setUp()

    def test_update_positions(self):
        self.test_approval_step_1.position = 88
        self.test_approval_step_1.save()
        self.test_approval_step_2.position = 55
        self.test_approval_step_2.save()
        self.test_approval_step_3.position = 22
        self.test_approval_step_3.save()
        self.test_approval_workflow.update_positions()
        self.test_approval_step_1.refresh_from_db()
        self.test_approval_step_2.refresh_from_db()
        self.test_approval_step_3.refresh_from_db()
        self.assertEqual(self.test_approval_step_1.position, 1)
        self.assertEqual(self.test_approval_step_2.position, 2)
        self.assertEqual(self.test_approval_step_3.position, 3)
