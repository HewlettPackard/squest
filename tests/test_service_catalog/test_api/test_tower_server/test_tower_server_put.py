from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.utils import check_data_in_dict


class TestApiAnsibleControllerPut(BaseTestRequest):

    def setUp(self):
        super(TestApiAnsibleControllerPut, self).setUp()
        self.put_data = {
            'name': "New Ansible controller server",
            'host': "my-ansible-controller-domain.com",
            'token': "mytokenverysimple",
            'secure': True,
            'ssl_verify': False,
            'extra_vars': {"test": "test"}
        }
        self.kwargs = {
            'pk': self.ansible_controller_test.id
        }
        self.ansible_controller_url = reverse('api_ansible_controller_details', kwargs=self.kwargs)

    def test_admin_put_ansible_controller(self):
        response = self.client.put(self.ansible_controller_url, data=self.put_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data_in_dict(self, [self.put_data], [response.data])

    def test_admin_cannot_put_on_ansible_controller_not_full(self):
        self.put_data.pop('name')
        response = self.client.put(self.ansible_controller_url, data=self.put_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_cannot_put_ansible_controller(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.put(self.ansible_controller_url, data=self.put_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_put_ansible_controller_when_logout(self):
        self.client.logout()
        response = self.client.put(self.ansible_controller_url, data=self.put_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
