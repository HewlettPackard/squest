from rest_framework import status
from rest_framework.reverse import reverse

from profiles.api.serializers.user_serializers import UserSerializer
from service_catalog.models import Request
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.utils import check_data_in_dict


class TestApiRequestDetails(BaseTestRequest):

    def setUp(self):
        super(TestApiRequestDetails, self).setUp()
        self.test_request_standard_user_1 = Request.objects.create(
            fill_in_survey={},
            instance=self.test_instance,
            operation=self.create_operation_test,
            user=self.standard_user
        )
        Request.objects.create(
            fill_in_survey={},
            instance=self.test_instance,
            operation=self.update_operation_test,
            user=self.standard_user
        )
        self.test_request_standard_user_2 = Request.objects.create(
            fill_in_survey={},
            instance=self.test_instance_2,
            operation=self.create_operation_test,
            user=self.standard_user_2
        )
        Request.objects.create(
            fill_in_survey={},
            instance=self.test_instance_2,
            operation=self.update_operation_test,
            user=self.standard_user_2
        )
        self.kwargs = {
            'pk': self.test_request_standard_user_1.id
        }
        self.get_request_details_url = reverse('api_request_details', kwargs=self.kwargs)
        self.expected_data = {
            'id': self.test_request_standard_user_1.id,
            'fill_in_survey': self.test_request_standard_user_1.fill_in_survey,
            'tower_job_id': self.test_request_standard_user_1.tower_job_id,
            'state': self.test_request_standard_user_1.state,
            'operation': self.test_request_standard_user_1.operation.id,
            'user': UserSerializer(instance=self.test_request_standard_user_1.user).data
        }
        self.expected_instance = {
            'id': self.test_request_standard_user_1.instance.id,
            'state': self.test_request_standard_user_1.instance.state,
            'name': self.test_request_standard_user_1.instance.name,
            'spec': self.test_request_standard_user_1.instance.spec,
            'service': self.test_request_standard_user_1.instance.service.id,
            'spoc': self.test_request_standard_user_1.instance.spoc.id,
            'billing_group': self.test_request_standard_user_1.instance.billing_group.id if self.test_request_standard_user_1.instance.billing_group else None
        }
        self.expected_data_list = [self.expected_data, self.expected_instance]

    def test_admin_get_request_detail(self):
        response = self.client.get(self.get_request_details_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_list = [response.data, response.data.get('instance', None)]
        check_data_in_dict(self, self.expected_data_list, data_list)

    def test_customer_get_his_request_detail(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.get_request_details_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_list = [response.data, response.data.get('instance', None)]
        check_data_in_dict(self, self.expected_data_list, data_list)

    def test_customer_cannot_get_non_own_request_detail(self):
        self.client.force_login(user=self.standard_user)
        self.kwargs['pk'] = self.test_request_standard_user_2.id
        url = reverse('api_request_details', kwargs=self.kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_get_request_details_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_request_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
