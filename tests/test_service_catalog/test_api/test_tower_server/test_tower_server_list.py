from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import AnsibleController
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestApiAnsibleControllerList(BaseTestRequest):

    def setUp(self):
        super(TestApiAnsibleControllerList, self).setUp()
        self.ansible_controller_url = reverse('api_ansible_controller_list_create')

    def test_admin_get_ansible_controller(self):
        response = self.client.get(self.ansible_controller_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("token", response.data['results'][0])
        self.assertEqual(response.data['count'], AnsibleController.objects.count())

    def test_customer_cannot_get_ansible_controller(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.ansible_controller_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_get_ansible_controller_list_when_logout(self):
        self.client.logout()
        response = self.client.get(self.ansible_controller_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
