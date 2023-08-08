from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.utils import check_data_in_dict


class TestApiAnsibleControllerDetails(BaseTestRequest):

    def setUp(self):
        super(TestApiAnsibleControllerDetails, self).setUp()
        self.kwargs = {
            'pk': self.ansible_controller_test.id
        }
        self.ansible_controller_url = reverse('api_ansible_controller_details', kwargs=self.kwargs)
        self.expected_data = {
            'id': self.ansible_controller_test.id,
            'name': self.ansible_controller_test.name,
            'host': self.ansible_controller_test.host,
            'secure': self.ansible_controller_test.secure,
            'ssl_verify': self.ansible_controller_test.ssl_verify,
            'extra_vars': dict()
        }
        self.expected_data_list = [self.expected_data]

    def test_admin_get_ansible_controller_detail(self):
        response = self.client.get(self.ansible_controller_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_list = [response.data]
        self.assertNotIn("token", data_list)
        check_data_in_dict(self, self.expected_data_list, data_list)

    def test_customer_cannot_get_ansible_controller_detail(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.ansible_controller_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_get_ansible_controller_details_when_logout(self):
        self.client.logout()
        response = self.client.get(self.ansible_controller_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
