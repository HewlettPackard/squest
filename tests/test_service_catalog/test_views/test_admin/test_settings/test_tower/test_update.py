from unittest import mock

from django.urls import reverse

from tests.test_service_catalog.test_views.test_admin.test_settings.test_tower.base_test_tower import BaseTestTower


class AdminTowerUpdateViewsTest(BaseTestTower):

    def setUp(self):
        super(AdminTowerUpdateViewsTest, self).setUp()
        self.args = {
            'tower_id': self.tower_server_test.id,
        }
        self.data = {
            "name": "tower-server-test-updated",
            "host": "https://tower-updated.domain.local",
            "token": "xxxx-updated"
        }
        self.url = reverse('service_catalog:update_tower', kwargs=self.args)

    def test_update_tower(self):
        with mock.patch("towerlib.towerlib.Tower.__init__") as mock_tower_lib:
            mock_tower_lib.return_value = None
            response = self.client.post(self.url, data=self.data)
            self.assertEquals(302, response.status_code)
            self.tower_server_test.refresh_from_db()
            self.assertEquals(self.tower_server_test.name, "tower-server-test-updated")
            self.assertEquals(self.tower_server_test.host, "tower-updated.domain.local")
            self.assertEquals(self.tower_server_test.token, "xxxx-updated")
