from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.utils import check_data_in_dict


class TestApiServicePatch(BaseTestRequest):

    def setUp(self):
        super(TestApiServicePatch, self).setUp()
        self.patch_data = {
            'name': "My new name",
            'description': "My new description",
        }
        self.kwargs = {
            'pk': self.service_test.id
        }
        self.get_service_details_url = reverse('api_service_details', kwargs=self.kwargs)
        self.expected_data = {
            'id': self.service_test.id,
            'name': "My new name",
            'description': "My new description",
            'image': f"http://testserver{self.service_test.image.url}",
            'enabled': self.service_test.enabled
        }

    def test_admin_patch_service(self):
        response = self.client.patch(self.get_service_details_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data_in_dict(self, [self.expected_data], [response.data])

    def test_customer_cannot_patch_service(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.patch(self.get_service_details_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_patch_service_when_logout(self):
        self.client.logout()
        response = self.client.patch(self.get_service_details_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
