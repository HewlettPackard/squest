from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequestAPI
from tests.utils import check_data_in_dict


class TestApiTowerServerPatch(BaseTestRequestAPI):

    def setUp(self):
        super(TestApiTowerServerPatch, self).setUp()
        self.patch_data = {
            'name': "New Tower Server",
            'token': "mytokenverysimple",
        }
        self.kwargs = {
            'pk': self.tower_server_test.id
        }
        self.tower_server_url = reverse('api_towerserver_details', kwargs=self.kwargs)
        self.expected_data = {
            'name': "New Tower Server",
            'host': self.tower_server_test.host,
            'token': "mytokenverysimple",
            'secure': self.tower_server_test.secure,
            'ssl_verify': self.tower_server_test.ssl_verify
        }

    def test_admin_patch_tower_server(self):
        response = self.client.patch(self.tower_server_url, data=self.patch_data,
                                     format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.expected_data.pop("token")
        check_data_in_dict(self, [self.expected_data], [response.data])

    def test_customer_cannot_patch_tower_server(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.patch(self.tower_server_url, data=self.patch_data,
                                     format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_patch_tower_server_when_logout(self):
        self.client.logout()
        response = self.client.patch(self.tower_server_url, data=self.patch_data,
                                     format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
