from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequestAPI
from tests.utils import check_data_in_dict


class TestApiServiceDetails(BaseTestRequestAPI):

    def setUp(self):
        super(TestApiServiceDetails, self).setUp()
        self.kwargs = {
            'pk': self.service_test.id
        }
        self.get_service_details_url = reverse('api_service_details', kwargs=self.kwargs)
        self.expected_data = {
            'id': self.service_test.id,
            'name': self.service_test.name,
            'description': self.service_test.description,
            'image': f"http://testserver{self.service_test.image.url}",
            'enabled': self.service_test.enabled,
            'extra_vars': dict()
        }
        self.expected_data_list = [self.expected_data]
        self.service_test_2.enabled = False
        self.service_test_2.save()

    def test_admin_get_service_detail(self):
        response = self.client.get(self.get_service_details_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_list = [response.data]
        check_data_in_dict(self, self.expected_data_list, data_list)

    def test_customer_get_service_detail(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.get_service_details_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_list = [response.data]
        check_data_in_dict(self, self.expected_data_list, data_list)

    def test_customer_cannot_get_detail_on_disabled_service(self):
        self.client.force_login(user=self.standard_user)
        self.kwargs['pk'] = self.service_test_2.id
        self.get_service_details_url = reverse('api_service_details', kwargs=self.kwargs)
        response = self.client.get(self.get_service_details_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_get_service_details_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_service_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
