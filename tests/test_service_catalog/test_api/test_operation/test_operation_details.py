from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.utils import check_data_in_dict


class TestApiOperationDetails(BaseTestRequest):

    def setUp(self):
        super(TestApiOperationDetails, self).setUp()
        self.kwargs = {
            'service_id': self.service_test.id,
            'pk': self.create_operation_test.id
        }
        self.get_operation_details_url = reverse('api_operation_details', kwargs=self.kwargs)
        self.expected_data = {
            'id': self.create_operation_test.id,
            'name': self.create_operation_test.name,
            'description': self.create_operation_test.description,
            'type': self.create_operation_test.type,
            'auto_accept': self.create_operation_test.auto_accept,
            'auto_process': self.create_operation_test.auto_process,
            'process_timeout_second': self.create_operation_test.process_timeout_second,
            'service': self.create_operation_test.service.id,
            'job_template': self.create_operation_test.job_template.id
        }
        self.expected_data_list = [self.expected_data]

    def test_admin_get_operation_detail(self):
        response = self.client.get(self.get_operation_details_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_list = [response.data]
        check_data_in_dict(self, self.expected_data_list, data_list)

    def test_customer_get_operation_detail(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.get_operation_details_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_list = [response.data]
        check_data_in_dict(self, self.expected_data_list, data_list)

    def test_cannot_get_request_details_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_operation_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
