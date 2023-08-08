from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import AnsibleController
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI
from tests.utils import check_data_in_dict


class AnsibleControllerCreate(BaseTestRequestAPI):

    def setUp(self):
        super(AnsibleControllerCreate, self).setUp()
        self.post_data = {
            'name': "New Ansible controller server",
            'host': "my-ansible-controller-domain.com",
            'token': "mytokenverysimple",
            'secure': True,
            'ssl_verify': False,
            'extra_vars': {"test": "test"}
        }
        self.ansible_controller_url = reverse('api_ansible_controller_list_create')

    def test_admin_post_ansible_controller(self):
        response = self.client.post(self.ansible_controller_url, data=self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        check_data_in_dict(self, [self.post_data], [response.data])
        ansible_controller = AnsibleController.objects.last()
        self.assertEqual(ansible_controller.name, self.post_data['name'])
        self.assertEqual(ansible_controller.host, self.post_data['host'])
        self.assertEqual(ansible_controller.token, self.post_data['token'])
        self.assertEqual(ansible_controller.secure, self.post_data['secure'])
        self.assertEqual(ansible_controller.ssl_verify, self.post_data['ssl_verify'])

    def test_admin_cannot_post_on_ansible_controller_without_host(self):
        self.post_data.pop('host')
        response = self.client.post(self.ansible_controller_url, data=self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_cannot_post_on_ansible_controller_not_full(self):
        self.post_data.pop('name')
        response = self.client.post(self.ansible_controller_url, data=self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_cannot_post_ansible_controller(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.post(self.ansible_controller_url, data=self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_post_ansible_controller_when_logout(self):
        self.client.logout()
        response = self.client.post(self.ansible_controller_url, data=self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_post_ansible_controller_with_non_json_as_extra_vars(self):
        self.post_data['extra_vars'] = "test"
        response = self.client.post(self.ansible_controller_url, data=self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
