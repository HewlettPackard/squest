from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.utils import check_data_in_dict


class TestApiAnsibleControllerPatch(BaseTestRequest):

    def setUp(self):
        super(TestApiAnsibleControllerPatch, self).setUp()
        self.patch_data = {
            'name': "New Ansible controller server",
            'token': "mytokenverysimple",
        }
        self.kwargs = {
            'pk': self.ansible_controller_test.id
        }
        self.ansible_controller_url = reverse('api_ansible_controller_details', kwargs=self.kwargs)
        self.expected_data = {
            'name': "New Ansible controller server",
            'host': self.ansible_controller_test.host,
            'token': "mytokenverysimple",
            'secure': self.ansible_controller_test.secure,
            'ssl_verify': self.ansible_controller_test.ssl_verify
        }

    def test_admin_patch_ansible_controller(self):
        response = self.client.patch(self.ansible_controller_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data_in_dict(self, [self.expected_data], [response.data])

    def test_customer_cannot_patch_ansible_controller(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.patch(self.ansible_controller_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_patch_ansible_controller_when_logout(self):
        self.client.logout()
        response = self.client.patch(self.ansible_controller_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
