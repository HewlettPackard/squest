from rest_framework.reverse import reverse

from service_catalog.models import ApprovalWorkflow, ApprovalStep
from tests.test_service_catalog.base_test_approval import BaseTestApprovalAPI


class TestApprovalWorkflowUpdateStepPositions(BaseTestApprovalAPI):

    def setUp(self):
        super(TestApprovalWorkflowUpdateStepPositions, self).setUp()
        self.url = reverse('api_approvalworkflow_update_steps_position', args=[self.test_approval_workflow.id])

        # approval
        self.test_approval_workflow_2 = ApprovalWorkflow.objects.create(name="test_approval_workflow_2",
                                                                        operation=self.update_operation_test)

        self.test_approval_step_3 = ApprovalStep.objects.create(name="test_approval_step_3",
                                                                approval_workflow=self.test_approval_workflow_2)

    def _assert_position_updated(self):
        self.test_approval_step_1.refresh_from_db()
        self.test_approval_step_2.refresh_from_db()
        self.assertEqual(1, self.test_approval_step_1.position)
        self.assertEqual(0, self.test_approval_step_2.position)

    def _assert_position_still_the_same(self):
        self.test_approval_step_1.refresh_from_db()
        self.test_approval_step_2.refresh_from_db()
        self.assertEqual(0, self.test_approval_step_1.position)
        self.assertEqual(1, self.test_approval_step_2.position)

    def test_set_position(self):
        data = [
            {"id": self.test_approval_step_1.id, "position": 1},
            {"id": self.test_approval_step_2.id, "position": 0},
        ]
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, 200)
        self._assert_position_updated()

    def test_set_position_invalid_step_id(self):
        data = [
            {"id": self.test_approval_step_1.id, "position": 1},
            {"id": self.test_approval_step_3.id, "position": 0},
        ]
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid Step Id For The Approval Workflow", response.data[0].title())
        self._assert_position_still_the_same()

    def test_set_position_missing_step(self):
        data = [
            {"id": self.test_approval_step_1.id, "position": 1},
        ]
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing Position", response.data[0].title())
        self._assert_position_still_the_same()

    def test_set_position_missing_position(self):
        data = [
            {"id": self.test_approval_step_1.id, "position": 0},
            {"id": self.test_approval_step_2.id, "position": 2},
        ]
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing Position 1", response.data[0].title())
        self._assert_position_still_the_same()
