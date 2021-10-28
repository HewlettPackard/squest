from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.utils import check_data_in_dict


class TestApiUserPatch(BaseTestRequest):

    def setUp(self):
        super(TestApiUserPatch, self).setUp()
        self.patch_data = {
            'username': "newUsername",
        }
        self.kwargs = {
            'pk': self.standard_user.id
        }
        self.get_user_details_url = reverse('api_user_details', kwargs=self.kwargs)
        self.expected_data = {
            'id': self.standard_user.id,
            'username': "newUsername",
            'email': self.standard_user.email,
            'first_name': self.standard_user.first_name,
            'last_name': self.standard_user.last_name,
            'is_staff': self.standard_user.is_staff,
            'is_superuser': self.standard_user.is_superuser,
            'is_active': self.standard_user.is_active,
            'groups': list(self.standard_user.groups.all()),
            'user_permissions': list(self.standard_user.user_permissions.all()),
        }

    def test_admin_patch_user(self):
        response = self.client.patch(self.get_user_details_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_data_in_dict(self, [self.expected_data], [response.data])

    def test_customer_cannot_patch_user(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.patch(self.get_user_details_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_patch_user_when_logout(self):
        self.client.logout()
        response = self.client.patch(self.get_user_details_url, data=self.patch_data,
                                     content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
