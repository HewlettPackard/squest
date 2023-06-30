from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import Service
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI
from tests.utils import check_data_in_dict


class TestApiServiceCreate(BaseTestRequestAPI):

    def setUp(self):
        super(TestApiServiceCreate, self).setUp()
        self.post_data = {
            'name': "My new name",
            'description': "My new description",
            'enabled': False,
            'extra_vars': {"test": "test"}
        }
        self.get_service_details_url = reverse('api_service_list_create')

    def test_admin_post_service(self):
        response = self.client.post(self.get_service_details_url, data=self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        check_data_in_dict(self, [self.post_data], [response.data])
        service = Service.objects.last()
        self.assertEqual(service.name, self.post_data['name'])

    def test_admin_cannot_post_on_service_not_full(self):
        self.post_data.pop('name')
        response = self.client.post(self.get_service_details_url, data=self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_cannot_post_service(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.post(self.get_service_details_url, data=self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_post_service_when_logout(self):
        self.client.logout()
        response = self.client.post(self.get_service_details_url, data=self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_post_service_with_non_json_as_extra_vars(self):
        self.post_data['extra_vars'] = 'test'
        response = self.client.post(self.get_service_details_url, data=self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
