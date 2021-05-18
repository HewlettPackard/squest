from unittest import mock

import requests
import towerlib
from django.urls import reverse

from service_catalog.models import TowerServer
from tests.test_views.admin.settings.tower.base_test_tower import BaseTestTower


class AdminTowerCreateViewsTest(BaseTestTower):

    def setUp(self):
        super(AdminTowerCreateViewsTest, self).setUp()
        self.url = reverse('add_tower')
        self.data = {
            "name": "tower1",
            "host": "https://tower.domain.local",
            "token": "xxxx"
        }

    def test_admin_can_create_tower_server(self):
        with mock.patch("towerlib.towerlib.Tower.__init__") as mock_tower_lib:
            mock_tower_lib.return_value = None
            response = self.client.post(self.url, data=self.data)
            self.assertEquals(302, response.status_code)
            self.assertEquals(2, TowerServer.objects.all().count())

    # @mock.patch.object(Tower, '__init__', requests.exceptions.ConnectionError)
    def test_connection_error_on_create(self):
        with mock.patch("towerlib.towerlib.Tower.__init__") as mock_tower_lib:
            mock_tower_lib.side_effect = requests.exceptions.ConnectionError
            response = self.client.post(self.url, data=self.data)
            self.assertEquals(1, TowerServer.objects.all().count())
            self.assertContains(response, "Unable to connect to https://tower.domain.local", status_code=200, html=False)

    def test_certificate_verify_failed_no_create(self):
        with mock.patch("towerlib.towerlib.Tower.__init__") as mock_tower_lib:
            mock_tower_lib.side_effect = requests.exceptions.SSLError
            response = self.client.post(self.url, data=self.data)
            self.assertEquals(1, TowerServer.objects.all().count())
            self.assertContains(response, "Certificate verify failed", status_code=200, html=False)

    def test_auth_failed_on_create(self):
        with mock.patch("towerlib.towerlib.Tower.__init__") as mock_tower_lib:
            mock_tower_lib.side_effect = towerlib.towerlibexceptions.AuthFailed
            response = self.client.post(self.url, data=self.data)
            self.assertEquals(1, TowerServer.objects.all().count())
            self.assertContains(response, "Fail to authenticate with provided token", status_code=200, html=False)
