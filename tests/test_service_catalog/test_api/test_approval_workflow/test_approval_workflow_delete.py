from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models.approval_workflow import ApprovalWorkflow
from tests.test_service_catalog.base_approval import BaseApproval


class TestApiApprovalWorkflowDelete(BaseApproval):

    def setUp(self):
        super(TestApiApprovalWorkflowDelete, self).setUp()
        self.approval_workflow_to_delete_id = self.test_approval_workflow.id
        self.delete_approval_workflow_url = reverse('api_approval_workflow_details',
                                                    kwargs={'pk': self.test_approval_workflow.id})
        self.approval_workflow_count = ApprovalWorkflow.objects.count()


    def test_admin_can_delete_approval_workflow(self):
        response = self.client.delete(self.delete_approval_workflow_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.approval_workflow_count - 1, ApprovalWorkflow.objects.count())
        self.assertFalse(ApprovalWorkflow.objects.filter(id=self.approval_workflow_to_delete_id).exists())

    def test_customer_cannot_delete_approval_workflow(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.delete(self.delete_approval_workflow_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.approval_workflow_count, ApprovalWorkflow.objects.count())

    def test_cannot_delete_approval_workflow_when_logout(self):
        self.client.logout()
        response = self.client.delete(self.delete_approval_workflow_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.approval_workflow_count, ApprovalWorkflow.objects.count())

