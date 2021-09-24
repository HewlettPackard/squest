from unittest import mock

import requests
import towerlib
from django.urls import reverse

from service_catalog.models import TowerServer
from tests.test_service_catalog.test_views.admin.settings.tower.base_test_tower import BaseTestTower


class AdminTowerCreateViewsTest(BaseTestTower):

    def setUp(self):
        super(AdminTowerCreateViewsTest, self).setUp()
        self.url = reverse('service_catalog:add_tower')
        self.data = {
            "name": "tower1",
            "host": "tower.domain.local",
            "token": "xxxx"
        }

        self.number_tower_before = TowerServer.objects.all().count()

    def test_admin_can_create_tower_server(self):
        test_url_list = [("http://tower0.domain.net/", "tower0.domain.net"),
                         ("http://tower1.domain.net", "tower1.domain.net"),
                         ("http://tower2.domain.net:8043", "tower2.domain.net:8043"),
                         ("http://tower3.domain.net:8043/", "tower3.domain.net:8043"),
                         ("https://tower4.domain.net/", "tower4.domain.net"),
                         ("https://tower5.domain.net", "tower5.domain.net"),
                         ("https://tower6.domain.net:8043", "tower6.domain.net:8043"),
                         ("https://tower7.domain.net:8043/", "tower7.domain.net:8043"),
                         ("tower8.domain.net/", "tower8.domain.net"),
                         ("tower9.domain.net", "tower9.domain.net"),
                         ("tower10.domain.net:8043", "tower10.domain.net:8043"),
                         ("tower11.domain.net:8043/", "tower11.domain.net:8043"),
                         ("tower12.domain.net:8043/tower", "tower12.domain.net:8043/tower"),
                         ("192.168.1.1", "192.168.1.1"),
                         ("192.168.1.2/tower", "192.168.1.2/tower"),
                         ("192.168.1.3:8043", "192.168.1.3:8043")]

        for index, tuple in enumerate(test_url_list):
            url = tuple[0]
            expected_host = tuple[1]
            name = f"tower-{index}"
            with mock.patch("towerlib.towerlib.Tower.__init__") as mock_tower_lib:
                with mock.patch("service_catalog.models.tower_server.TowerServer.sync") as mock_tower_sync:
                    mock_tower_lib.return_value = None
                    data = {
                        "name": name,
                        "host": url,
                        "token": "xxxx"
                    }
                    response = self.client.post(self.url, data=data)
                    self.assertEquals(302, response.status_code)
                    self.assertEquals(self.number_tower_before + 1, TowerServer.objects.all().count())
                    mock_tower_sync.assert_called()
                    self.number_tower_before = self.number_tower_before + 1
                    self.assertTrue(TowerServer.objects.filter(name=name).exists())
                    new_tower = TowerServer.objects.get(name=name)
                    self.assertEquals(name, new_tower.name)
                    self.assertEquals(expected_host, new_tower.host)

    def test_connection_error_on_create(self):
        with mock.patch("towerlib.towerlib.Tower.__init__") as mock_tower_lib:
            mock_tower_lib.side_effect = requests.exceptions.ConnectionError
            response = self.client.post(self.url, data=self.data)
            self.assertEquals(self.number_tower_before, TowerServer.objects.all().count())
            self.assertContains(response, "Unable to connect to tower.domain.local",
                                status_code=200, html=False)

    def test_certificate_verify_failed_no_create(self):
        with mock.patch("towerlib.towerlib.Tower.__init__") as mock_tower_lib:
            mock_tower_lib.side_effect = requests.exceptions.SSLError
            response = self.client.post(self.url, data=self.data)
            self.assertEquals(self.number_tower_before, TowerServer.objects.all().count())
            self.assertContains(response, "Certificate verify failed", status_code=200, html=False)

    def test_auth_failed_on_create(self):
        with mock.patch("towerlib.towerlib.Tower.__init__") as mock_tower_lib:
            mock_tower_lib.side_effect = towerlib.towerlibexceptions.AuthFailed
            response = self.client.post(self.url, data=self.data)
            self.assertEquals(self.number_tower_before, TowerServer.objects.all().count())
            self.assertContains(response, "Fail to authenticate with provided token", status_code=200, html=False)

    def test_user_cannot_create_tower_server(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        response = self.client.post(self.url, data=self.data)
        self.assertEquals(302, response.status_code)
        self.assertEquals(self.number_tower_before, TowerServer.objects.all().count())
