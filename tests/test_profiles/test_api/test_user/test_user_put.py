from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.utils import check_data_in_dict


class TestApiUserPatch(BaseTestRequest):

    def setUp(self):
        super(TestApiUserPatch, self).setUp()
        self.put_data = {
            'username': "myUsername",
            'password': "password",
        }
        self.kwargs = {
            'pk': self.standard_user.id
        }
        self.get_user_details_url = reverse('api_user_details', kwargs=self.kwargs)
        self.expected_data = {
            'id': self.standard_user.id,
            'username': "myUsername",
            'email': self.standard_user.email,
            'first_name': self.standard_user.first_name,
            'last_name': self.standard_user.last_name,
            'is_staff': self.standard_user.is_staff,
            'is_superuser': self.standard_user.is_superuser,
            'is_active': self.standard_user.is_active,
        }

    def test_admin_put_user(self):
        old_password = self.standard_user.password
        response = self.client.put(self.get_user_details_url, data=self.put_data,
                                   content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.standard_user.refresh_from_db()
        self.assertNotEqual(old_password, self.standard_user.password)
        check_data_in_dict(self, [self.expected_data], [response.data])

    def test_customer_cannot_put_user(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.put(self.get_user_details_url, data=self.put_data,
                                   content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_put_user_when_logout(self):
        self.client.logout()
        response = self.client.put(self.get_user_details_url, data=self.put_data,
                                   content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
