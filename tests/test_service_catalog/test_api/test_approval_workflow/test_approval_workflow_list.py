from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models.approval_workflow import ApprovalWorkflow
from tests.test_service_catalog.base_approval import BaseApproval


class TestApiApprovalWorkflowList(BaseApproval):

    def setUp(self):
        super(TestApiApprovalWorkflowList, self).setUp()
        self.get_approval_workflow_list_url = reverse('api_approval_workflow_list_create')

    def test_get_all_approval_workflows(self):
        response = self.client.get(self.get_approval_workflow_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), ApprovalWorkflow.objects.count())

    def test_customer_cannot_get_approval_workflow_list(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.get_approval_workflow_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_get_approval_workflow_list_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_approval_workflow_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
