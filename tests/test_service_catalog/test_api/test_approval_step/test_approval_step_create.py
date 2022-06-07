from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import ApprovalWorkflow
from service_catalog.models.approval_step_type import ApprovalStepType
from tests.test_service_catalog.base_approval import BaseApproval
from tests.utils import check_data_in_dict


class TestApiApprovalStepCreate(BaseApproval):

    def setUp(self):
        super(TestApiApprovalStepCreate, self).setUp()
        self.post_data = {
            "name": "new_approval_step_name",
            "type": ApprovalStepType.AT_LEAST_ONE,
            "teams": [self.test_team.id],
            "next": None,
        }
        self.create_approval_step_url = reverse('api_approval_step_list_create',
                                                kwargs={'approval_workflow_id': self.test_approval_workflow.id})

    def _create_approval_step(self):
        response = self.client.post(self.create_approval_step_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        check_data_in_dict(self, [self.post_data], [response.data])
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertIn("type", response.data)
        self.assertIn("teams", response.data)
        self.assertIn("next", response.data)

    def _create_approval_step_failed(self, status_error=status.HTTP_400_BAD_REQUEST):
        response = self.client.post(self.create_approval_step_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status_error)

    def test_admin_can_create_approval_step_in_workflow_without_entry_point(self):
        new_workflow = ApprovalWorkflow.objects.create(name="test new approval workflow")
        self.create_approval_step_url = reverse('api_approval_step_list_create',
                                                kwargs={'approval_workflow_id': new_workflow.id})
        self._create_approval_step()

    def test_admin_cannot_create_approval_step_in_workflow_with_entry_point(self):
        response = self.client.post(self.create_approval_step_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_create_approval_step(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.post(self.create_approval_step_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_create_approval_step_when_logout(self):
        self.client.logout()
        response = self.client.post(self.create_approval_step_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
