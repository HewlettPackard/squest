from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.utils import check_data_in_dict


class TestApiTowerServerPut(BaseTestRequest):

    def setUp(self):
        super(TestApiTowerServerPut, self).setUp()
        self.put_data = {
            'name': "New Tower Server",
            'host': "my-tower-domain.com",
            'token': "mytokenverysimple",
            'secure': True,
            'ssl_verify': False,
            'extra_vars': {"test": "test"}
        }
        self.kwargs = {
            'pk': self.tower_server_test.id
        }
        self.tower_server_url = reverse('api_tower_server_details', kwargs=self.kwargs)

    def test_admin_put_tower_server(self):
        response = self.client.put(self.tower_server_url, data=self.put_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data_in_dict(self, [self.put_data], [response.data])

    def test_admin_cannot_put_on_tower_server_not_full(self):
        self.put_data.pop('name')
        response = self.client.put(self.tower_server_url, data=self.put_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_cannot_put_tower_server(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.put(self.tower_server_url, data=self.put_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_put_tower_server_when_logout(self):
        self.client.logout()
        response = self.client.put(self.tower_server_url, data=self.put_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
