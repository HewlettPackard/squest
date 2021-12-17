from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import TowerServer
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestApiTowerServerList(BaseTestRequest):

    def setUp(self):
        super(TestApiTowerServerList, self).setUp()
        self.tower_server_url = reverse('api_tower_server_list_create')

    def test_admin_get_tower_server(self):
        response = self.client.get(self.tower_server_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("token", response.data[0])
        self.assertEqual(len(response.data), TowerServer.objects.count())

    def test_customer_cannot_get_tower_server(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.tower_server_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_get_tower_server_list_when_logout(self):
        self.client.logout()
        response = self.client.get(self.tower_server_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
