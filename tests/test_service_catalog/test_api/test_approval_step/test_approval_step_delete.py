from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models.approval_step import ApprovalStep
from tests.test_service_catalog.base_approval import BaseApproval


class TestApiApprovalStepDelete(BaseApproval):

    def setUp(self):
        super(TestApiApprovalStepDelete, self).setUp()
        self.approval_step_to_delete_id = self.test_approval_step_1.id
        self.delete_approval_step_url = reverse('api_approval_step_details', kwargs={
            'approval_workflow_id': self.test_approval_workflow.id,
            'pk': self.approval_step_to_delete_id
        })

    def test_admin_can_delete_entry_point_approval_step(self):
        approval_step_count = ApprovalStep.objects.count()
        response = self.client.delete(self.delete_approval_step_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(approval_step_count - 1, ApprovalStep.objects.count())
        self.assertFalse(ApprovalStep.objects.filter(id=self.approval_step_to_delete_id).exists())
        self.test_approval_workflow.refresh_from_db()
        self.assertEqual(self.test_approval_workflow.entry_point, self.test_approval_step_2)

    def test_admin_can_delete_approval_step_between_two_step(self):
        self.approval_step_to_delete_id = self.test_approval_step_2.id
        self.delete_approval_step_url = reverse('api_approval_step_details', kwargs={
            'approval_workflow_id': self.test_approval_workflow.id,
            'pk': self.approval_step_to_delete_id
        })
        approval_step_count = ApprovalStep.objects.count()
        response = self.client.delete(self.delete_approval_step_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(approval_step_count - 1, ApprovalStep.objects.count())
        self.assertFalse(ApprovalStep.objects.filter(id=self.approval_step_to_delete_id).exists())
        self.test_approval_step_1.refresh_from_db()
        self.assertEqual(self.test_approval_step_1.next, self.test_approval_step_3)

    def test_customer_cannot_delete_approval_step(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.delete(self.delete_approval_step_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_delete_approval_step_when_logout(self):
        self.client.logout()
        response = self.client.delete(self.delete_approval_step_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
