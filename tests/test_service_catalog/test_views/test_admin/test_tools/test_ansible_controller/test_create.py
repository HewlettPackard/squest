from unittest import mock

import requests
import towerlib
from django.urls import reverse

from service_catalog.models import AnsibleController
from tests.test_service_catalog.test_views.test_admin.test_tools.test_ansible_controller.base_test_ansible_controller import BaseTestAnsibleController


class AdminAnsibleControllerCreateViewsTest(BaseTestAnsibleController):

    def setUp(self):
        super(AdminAnsibleControllerCreateViewsTest, self).setUp()
        self.url = reverse('service_catalog:ansiblecontroller_create')
        self.data = {
            "name": "ansible-controller1",
            "host": "ansible-controller.domain.local",
            "token": "xxxx",
            "extra_vars": "{}"
        }

        self.number_ansiblecontroller_before = AnsibleController.objects.all().count()

    def test_get_page(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_admin_can_create_ansible_controller(self):
        test_url_list = [("http://ansible-controller0.domain.net/", "ansible-controller0.domain.net"),
                         ("http://ansible-controller1.domain.net", "ansible-controller1.domain.net"),
                         ("http://ansible-controller2.domain.net:8043", "ansible-controller2.domain.net:8043"),
                         ("http://ansible-controller3.domain.net:8043/", "ansible-controller3.domain.net:8043"),
                         ("https://ansible-controller4.domain.net/", "ansible-controller4.domain.net"),
                         ("https://ansible-controller5.domain.net", "ansible-controller5.domain.net"),
                         ("https://ansible-controller6.domain.net:8043", "ansible-controller6.domain.net:8043"),
                         ("https://ansible-controller7.domain.net:8043/", "ansible-controller7.domain.net:8043"),
                         ("ansible-controller8.domain.net/", "ansible-controller8.domain.net"),
                         ("ansible-controller9.domain.net", "ansible-controller9.domain.net"),
                         ("ansible-controller10.domain.net:8043", "ansible-controller10.domain.net:8043"),
                         ("ansible-controller11.domain.net:8043/", "ansible-controller11.domain.net:8043"),
                         ("ansible-controller12.domain.net:8043/ansible-controller", "ansible-controller12.domain.net:8043/ansible-controller"),
                         ("192.168.1.1", "192.168.1.1"),
                         ("192.168.1.2/ansible-controller", "192.168.1.2/ansible-controller"),
                         ("192.168.1.3:8043", "192.168.1.3:8043")]

        for index, tuple in enumerate(test_url_list):
            url = tuple[0]
            expected_host = tuple[1]
            name = f"ansible-controller-{index}"
            with mock.patch("towerlib.towerlib.Tower.__init__") as mock_tower_lib:
                with mock.patch("service_catalog.models.ansiblecontroller.AnsibleController.sync") as mock_ansible_controller_sync:
                    mock_tower_lib.return_value = None
                    data = {
                        "name": name,
                        "host": url,
                        "token": "xxxx"
                    }
                    response = self.client.post(self.url, data=data)
                    self.assertEqual(302, response.status_code)
                    self.assertEqual(self.number_ansiblecontroller_before + 1, AnsibleController.objects.all().count())
                    mock_ansible_controller_sync.assert_called()
                    self.number_ansiblecontroller_before = self.number_ansiblecontroller_before + 1
                    self.assertTrue(AnsibleController.objects.filter(name=name).exists())
                    new_ansible_controller = AnsibleController.objects.get(name=name)
                    self.assertEqual(name, new_ansible_controller.name)
                    self.assertEqual(expected_host, new_ansible_controller.host)

    def test_connection_error_on_create(self):
        with mock.patch("towerlib.towerlib.Tower.__init__") as mock_tower_lib:
            mock_tower_lib.side_effect = requests.exceptions.ConnectionError
            response = self.client.post(self.url, data=self.data)
            self.assertEqual(self.number_ansiblecontroller_before, AnsibleController.objects.all().count())
            self.assertContains(response, "Unable to connect to ansible-controller.domain.local",
                                status_code=200, html=False)

    def test_certificate_verify_failed_no_create(self):
        with mock.patch("towerlib.towerlib.Tower.__init__") as mock_tower_lib:
            mock_tower_lib.side_effect = requests.exceptions.SSLError
            response = self.client.post(self.url, data=self.data)
            self.assertEqual(self.number_ansiblecontroller_before, AnsibleController.objects.all().count())
            self.assertContains(response, "Certificate verify failed", status_code=200, html=False)

    def test_auth_failed_on_create(self):
        with mock.patch("towerlib.towerlib.Tower.__init__") as mock_tower_lib:
            mock_tower_lib.side_effect = towerlib.towerlibexceptions.AuthFailed
            response = self.client.post(self.url, data=self.data)
            self.assertEqual(self.number_ansiblecontroller_before, AnsibleController.objects.all().count())
            self.assertContains(response, "Fail to authenticate with provided token", status_code=200, html=False)

    def test_user_cannot_create_ansible_controller(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(403, response.status_code)
        self.assertEqual(self.number_ansiblecontroller_before, AnsibleController.objects.all().count())
