from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequestAPI
from tests.utils import check_data_in_dict


class TestApiServicePut(BaseTestRequestAPI):

    def setUp(self):
        super(TestApiServicePut, self).setUp()
        self.put_data = {
            'name': "My new name",
            'description': "My new description",
            'enabled': self.service_test.enabled,
            'extra_vars': {"test": "test"}
        }
        self.kwargs = {
            'pk': self.service_test.id
        }
        self.get_service_details_url = reverse('api_service_details', kwargs=self.kwargs)

    def test_admin_put_service(self):
        response = self.client.put(self.get_service_details_url, data=self.put_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data_in_dict(self, [self.put_data], [response.data])

    def test_admin_cannot_put_on_service_not_full(self):
        self.put_data.pop('name')
        response = self.client.put(self.get_service_details_url, data=self.put_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_cannot_put_service(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.put(self.get_service_details_url, data=self.put_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_put_service_when_logout(self):
        self.client.logout()
        response = self.client.put(self.get_service_details_url, data=self.put_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
