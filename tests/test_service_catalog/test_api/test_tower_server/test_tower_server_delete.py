from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import TowerServer
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestApiTowerServerDelete(BaseTestRequest):

    def setUp(self):
        super(TestApiTowerServerDelete, self).setUp()
        empty_tower = TowerServer.objects.create(name="test", host="tsst", token="test")
        self.tower_server_to_delete_id = empty_tower.id
        self.kwargs = {
            'pk': self.tower_server_to_delete_id
        }
        self.tower_server_url = reverse('api_tower_server_details', kwargs=self.kwargs)

    def test_admin_delete_request(self):
        tower_server_count = TowerServer.objects.count()
        response = self.client.delete(self.tower_server_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(tower_server_count - 1, TowerServer.objects.count())
        self.assertFalse(TowerServer.objects.filter(id=self.tower_server_to_delete_id).exists())

    def test_customer_cannot_delete_request(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.delete(self.tower_server_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_delete_request_when_logout(self):
        self.client.logout()
        response = self.client.delete(self.tower_server_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
