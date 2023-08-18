from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import TowerServer
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI
from tests.utils import check_data_in_dict


class TowerServerCreate(BaseTestRequestAPI):

    def setUp(self):
        super(TowerServerCreate, self).setUp()
        self.post_data = {
            'name': "New Tower Server",
            'host': "my-tower-domain.com",
            'token': "mytokenverysimple",
            'secure': True,
            'ssl_verify': False,
            'extra_vars': {"test": "test"}
        }
        self.tower_server_url = reverse('api_towerserver_list_create')

    def test_admin_post_tower_server(self):
        response = self.client.post(self.tower_server_url, data=self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        check_data_in_dict(self, [self.post_data], [response.data])
        tower_server = TowerServer.objects.last()
        self.assertEqual(tower_server.name, self.post_data['name'])
        self.assertEqual(tower_server.host, self.post_data['host'])
        self.assertEqual(tower_server.token, self.post_data['token'])
        self.assertEqual(tower_server.secure, self.post_data['secure'])
        self.assertEqual(tower_server.ssl_verify, self.post_data['ssl_verify'])

    def test_admin_cannot_post_on_tower_server_without_host(self):
        self.post_data.pop('host')
        response = self.client.post(self.tower_server_url, data=self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_cannot_post_on_tower_server_not_full(self):
        self.post_data.pop('name')
        response = self.client.post(self.tower_server_url, data=self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_cannot_post_tower_server(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.post(self.tower_server_url, data=self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_post_tower_server_when_logout(self):
        self.client.logout()
        response = self.client.post(self.tower_server_url, data=self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_post_tower_server_with_non_json_as_extra_vars(self):
        self.post_data['extra_vars'] = "test"
        response = self.client.post(self.tower_server_url, data=self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
