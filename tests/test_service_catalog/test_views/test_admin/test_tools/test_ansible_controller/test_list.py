from django.urls import reverse

from service_catalog.models import AnsibleController
from tests.test_service_catalog.test_views.test_admin.test_tools.test_ansible_controller.base_test_ansible_controller import BaseTestAnsibleController


class AdminAnsibleControllerListViewsTest(BaseTestAnsibleController):

    def setUp(self):
        super(AdminAnsibleControllerListViewsTest, self).setUp()
        self.url = reverse('service_catalog:ansiblecontroller_list')

    def test_admin_can_list_ansible_controller(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(AnsibleController.objects.count(), len(response.context["table"].data.data))

    def test_cannot_get_ansible_controller_list_when_logout(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(302, response.status_code)

    def test_user_cannot_list_ansible_controller(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)
