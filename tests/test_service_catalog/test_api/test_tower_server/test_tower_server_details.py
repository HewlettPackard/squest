from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.utils import check_data_in_dict


class TestApiTowerServerDetails(BaseTestRequest):

    def setUp(self):
        super(TestApiTowerServerDetails, self).setUp()
        self.kwargs = {
            'pk': self.tower_server_test.id
        }
        self.tower_server_url = reverse('api_tower_server_details', kwargs=self.kwargs)
        self.expected_data = {
            'id': self.tower_server_test.id,
            'name': self.tower_server_test.name,
            'host': self.tower_server_test.host,
            'secure': self.tower_server_test.secure,
            'ssl_verify': self.tower_server_test.ssl_verify
        }
        self.expected_data_list = [self.expected_data]

    def test_admin_get_tower_server_detail(self):
        response = self.client.get(self.tower_server_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_list = [response.data]
        self.assertNotIn("token", data_list)
        check_data_in_dict(self, self.expected_data_list, data_list)

    def test_customer_cannot_get_tower_server_detail(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.tower_server_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_get_tower_server_details_when_logout(self):
        self.client.logout()
        response = self.client.get(self.tower_server_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
