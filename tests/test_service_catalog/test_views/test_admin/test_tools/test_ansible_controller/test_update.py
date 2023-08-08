from unittest import mock

from django.urls import reverse

from tests.test_service_catalog.test_views.test_admin.test_tools.test_ansible_controller.base_test_ansible_controller import BaseTestAnsibleController


class AdminAnsibleControllerUpdateViewsTest(BaseTestAnsibleController):

    def setUp(self):
        super(AdminAnsibleControllerUpdateViewsTest, self).setUp()
        self.args = {
            'pk': self.ansible_controller_test.id,
        }
        self.data = {
            "name": "ansible-controller-server-test-updated",
            "host": "https://ansible-controller-updated.domain.local",
            "token": "xxxx-updated"
        }
        self.url = reverse('service_catalog:ansiblecontroller_edit', kwargs=self.args)

    def test_get_page(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_ansiblecontroller_edit(self):
        with mock.patch("towerlib.towerlib.Tower.__init__") as mock_tower_lib:
            mock_tower_lib.return_value = None
            response = self.client.post(self.url, data=self.data)
            self.assertEqual(302, response.status_code)
            self.ansible_controller_test.refresh_from_db()
            self.assertEqual(self.ansible_controller_test.name, "ansible-controller-server-test-updated")
            self.assertEqual(self.ansible_controller_test.host, "ansible-controller-updated.domain.local")
            self.assertEqual(self.ansible_controller_test.token, "xxxx-updated")
