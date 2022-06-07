from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import ApprovalWorkflow
from tests.test_service_catalog.base_approval import BaseApproval
from tests.utils import check_data_in_dict


class TestApiApprovalWorkflowCreate(BaseApproval):

    def setUp(self):
        super(TestApiApprovalWorkflowCreate, self).setUp()
        self.post_data = {
            "name": "new_approval_workflow_name",
        }
        self.create_approval_workflow_url = reverse('api_approval_workflow_list_create')

    def _create_approval_workflow(self):
        old_count = ApprovalWorkflow.objects.count()
        response = self.client.post(self.create_approval_workflow_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        check_data_in_dict(self, [self.post_data], [response.data])
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertIn("entry_point", response.data)
        self.assertEqual(old_count + 1, ApprovalWorkflow.objects.count())

    def _create_approval_workflow_failed(self, status_error=status.HTTP_400_BAD_REQUEST):
        old_count = ApprovalWorkflow.objects.count()
        response = self.client.post(self.create_approval_workflow_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status_error)
        self.assertEqual(old_count, ApprovalWorkflow.objects.count())

    def test_admin_can_create_approval_workflow(self):
        self.create_approval_workflow_url = reverse('api_approval_workflow_list_create')
        self._create_approval_workflow()

    def test_customer_cannot_create_approval_workflow(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.post(self.create_approval_workflow_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_create_approval_workflow_when_logout(self):
        self.client.logout()
        response = self.client.post(self.create_approval_workflow_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
