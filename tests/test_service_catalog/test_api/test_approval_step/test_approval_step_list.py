from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models.approval_step import ApprovalStep
from tests.test_service_catalog.base_approval import BaseApproval


class TestApiApprovalStepList(BaseApproval):

    def setUp(self):
        super(TestApiApprovalStepList, self).setUp()
        self.get_approval_step_list_url = reverse('api_approval_step_list_create',
                                                  kwargs={'approval_workflow_id': self.test_approval_workflow.id})

    def test_get_all_approval_steps(self):
        response = self.client.get(self.get_approval_step_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), ApprovalStep.objects.count())

    def test_customer_cannot_get_approval_step_list(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.get_approval_step_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_get_approval_step_list_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_approval_step_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
