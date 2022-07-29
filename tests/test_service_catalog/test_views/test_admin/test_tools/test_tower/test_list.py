from django.urls import reverse

from service_catalog.models import TowerServer
from tests.test_service_catalog.test_views.test_admin.test_tools.test_tower.base_test_tower import BaseTestTower


class AdminTowerListViewsTest(BaseTestTower):

    def setUp(self):
        super(AdminTowerListViewsTest, self).setUp()
        self.url = reverse('service_catalog:list_tower')

    def test_admin_can_list_tower_server(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(TowerServer.objects.count(), len(response.context["table"].data.data))

    def test_cannot_get_tower_server_list_when_logout(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(302, response.status_code)

    def test_user_cannot_list_tower_server(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)
