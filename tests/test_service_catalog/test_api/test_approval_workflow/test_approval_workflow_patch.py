from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.api.serializers.approval_workflow_serializer import ApprovalWorkflowSerializer
from tests.test_service_catalog.base_approval import BaseApproval
from tests.utils import check_data_in_dict


class TestApiApprovalWorkflowPatch(BaseApproval):

    def setUp(self):
        super(TestApiApprovalWorkflowPatch, self).setUp()
        self.patch_data = {
            'name': "My new approval workflow",
        }
        self.kwargs = {
            'pk': self.test_approval_workflow.id
        }
        self.get_approval_workflow_details_url = reverse('api_approval_workflow_details', kwargs=self.kwargs)
        self.expected_data = ApprovalWorkflowSerializer(self.test_approval_workflow).data
        self.expected_data['name'] = "My new approval workflow"

    def test_admin_patch_approval_workflow(self):
        response = self.client.patch(self.get_approval_workflow_details_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data_in_dict(self, [self.expected_data], [response.data])

    def test_customer_cannot_patch_approval_workflow(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.patch(self.get_approval_workflow_details_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_patch_approval_workflow_when_logout(self):
        self.client.logout()
        response = self.client.patch(self.get_approval_workflow_details_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
