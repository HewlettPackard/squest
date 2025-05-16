from unittest import mock

from django.urls import reverse

from tests.test_service_catalog.test_views.test_admin.test_tools.test_tower.base_test_tower import BaseTestTower


class AdminTowerUpdateViewsTest(BaseTestTower):

    def setUp(self):
        super(AdminTowerUpdateViewsTest, self).setUp()
        self.args = {
            'pk': self.tower_server_test.id,
        }
        self.data = {
            "name": "tower-server-test-updated",
            "host": "https://tower-updated.domain.local",
        }
        self.url = reverse('service_catalog:towerserver_edit', kwargs=self.args)

    def test_get_page(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_towerserver_edit(self):
        with mock.patch("towerlib.towerlib.Tower.__init__") as mock_tower_lib:
            mock_tower_lib.return_value = None
            response = self.client.post(self.url, data=self.data)
            self.assertEqual(302, response.status_code)
            self.tower_server_test.refresh_from_db()
            self.assertEqual(self.tower_server_test.name, "tower-server-test-updated")
            self.assertEqual(self.tower_server_test.host, "tower-updated.domain.local")


    def test_towerserver_update_token(self):
        self.url = reverse('service_catalog:towerserver_update_token', kwargs=self.args)
        self.data = {
            "name": "tower-server-test-updated",
            "host": "https://tower-updated.domain.local",
            "token": "xxxx-updated"
        }
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(302, response.status_code)
        self.tower_server_test.refresh_from_db()
        self.assertEqual(self.tower_server_test.token, "xxxx-updated")
