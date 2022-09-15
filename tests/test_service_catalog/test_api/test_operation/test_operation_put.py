from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.utils import check_data_in_dict


class TestApiOperationPut(BaseTestRequest):

    def setUp(self):
        super(TestApiOperationPut, self).setUp()
        self.put_data = {
            'name': "My new name",
            'description': "My new description",
            'type': self.create_operation_test.type,
            'auto_accept': self.create_operation_test.auto_accept,
            'auto_process': self.create_operation_test.auto_process,
            'process_timeout_second': self.create_operation_test.process_timeout_second,
            'service': self.create_operation_test.service.id,
            'job_template': self.create_operation_test.job_template.id,
            'extra_vars': '{"test": "test"}'
        }
        self.kwargs = {
            'service_id': self.service_test.id,
            'pk': self.create_operation_test.id
        }
        self.get_operation_details_url = reverse('api_operation_details', kwargs=self.kwargs)

    def test_admin_put_operation(self):
        response = self.client.put(self.get_operation_details_url, data=self.put_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data_in_dict(self, [self.put_data], [response.data])

    def test_admin_cannot_put_on_operation_not_full(self):
        self.put_data.pop('name')
        response = self.client.put(self.get_operation_details_url, data=self.put_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_cannot_put_operation(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.put(self.get_operation_details_url, data=self.put_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_put_operation_when_logout(self):
        self.client.logout()
        response = self.client.put(self.get_operation_details_url, data=self.put_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
