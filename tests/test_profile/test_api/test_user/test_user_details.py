from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.utils import check_data_in_dict


class TestApiUserDetails(BaseTestRequest):

    def setUp(self):
        super(TestApiUserDetails, self).setUp()
        self.kwargs = {
            'pk': self.standard_user.id
        }
        self.get_user_details_url = reverse('api_user_details', kwargs=self.kwargs)
        self.expected_data = {
            'id': self.standard_user.id,
            'email': self.standard_user.email,
            'first_name': self.standard_user.first_name,
            'last_name': self.standard_user.last_name,
            'username': self.standard_user.username,
            'is_staff': self.standard_user.is_staff,
            'is_superuser': self.standard_user.is_superuser,
            'is_active': self.standard_user.is_active,
            'groups': list(self.standard_user.groups.all()),
            'user_permissions': list(self.standard_user.user_permissions.all()),
        }
        self.expected_data_list = [self.expected_data]

    def test_admin_get_user_detail(self):
        response = self.client.get(self.get_user_details_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_list = [response.data]
        check_data_in_dict(self, self.expected_data_list, data_list)

    def test_customer_cannot_get_user_detail(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.get_user_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_get_request_details_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_user_details_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
