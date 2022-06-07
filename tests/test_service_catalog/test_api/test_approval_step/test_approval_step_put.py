from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.api.serializers.approval_step_serializer import ApprovalStepSerializer
from service_catalog.models.approval_step_type import ApprovalStepType
from tests.test_service_catalog.base_approval import BaseApproval
from tests.utils import check_data_in_dict


class TestApiApprovalStepPut(BaseApproval):

    def setUp(self):
        super(TestApiApprovalStepPut, self).setUp()
        self.put_data = {
            "name": "My new approval step",
            "type": ApprovalStepType.ALL_OF_THEM,
            "teams": [self.test_team2.id],
        }
        self.kwargs = {
            'approval_workflow_id': self.test_approval_workflow.id,
            'pk': self.test_approval_step_1.id
        }
        self.get_approval_step_details_url = reverse('api_approval_step_details', kwargs=self.kwargs)
        self.expected_data = ApprovalStepSerializer(self.test_approval_step_1).data
        self.expected_data["name"] = "My new approval step"
        self.expected_data["type"] = ApprovalStepType.ALL_OF_THEM
        self.expected_data["teams"] = [self.test_team2.id]
        self.expected_data["next"] = self.test_approval_step_1.next.id

    def test_admin_put_approval_step(self):
        response = self.client.put(self.get_approval_step_details_url, data=self.put_data,
                                   content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data_in_dict(self, [self.expected_data], [response.data])

    def test_customer_cannot_put_approval_step(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.put(self.get_approval_step_details_url, data=self.put_data,
                                   content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_put_approval_step_when_logout(self):
        self.client.logout()
        response = self.client.put(self.get_approval_step_details_url, data=self.put_data,
                                   content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
