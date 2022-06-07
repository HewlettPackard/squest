from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_approval import BaseApproval
from tests.utils import check_data_in_dict


class TestApiApprovalStepDetails(BaseApproval):

    def setUp(self):
        super(TestApiApprovalStepDetails, self).setUp()
        self.kwargs = {
            'approval_workflow_id': self.test_approval_workflow.id,
            'pk': self.test_approval_step_1.id
        }
        self.get_approval_step_details_url = reverse('api_approval_step_details', kwargs=self.kwargs)
        self.expected_data = {
            'id': self.test_approval_step_1.id,
            'name': self.test_approval_step_1.name,
            "type": self.test_approval_step_1.type,
            "teams": [team.id for team in self.test_approval_step_1.teams.all()],
            "next": self.test_approval_step_1.next.id,
        }
        self.expected_data_list = [self.expected_data]

    def test_admin_get_approval_step_detail(self):
        response = self.client.get(self.get_approval_step_details_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_list = [response.data]
        check_data_in_dict(self, self.expected_data_list, data_list)

    def test_customer_cannot_get_approval_step_detail(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.get_approval_step_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_get_request_details_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_approval_step_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
