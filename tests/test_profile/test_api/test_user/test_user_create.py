from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestApiUserCreate(BaseTestRequest):

    def setUp(self):
        super(TestApiUserCreate, self).setUp()
        self.post_data = {
            'username': "myUsername",
            'password': "password",
        }
        self.create_user_url = reverse('api_user_list_create')

    def _create_user(self):
        response = self.client.post(self.create_user_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data.keys()),
                         {'id', 'last_name', 'first_name', 'is_staff', 'email',
                          'profile', 'username', 'is_superuser', 'is_active', 'billing_groups'})

    def _create_user_failed(self, status_error=status.HTTP_400_BAD_REQUEST):
        response = self.client.post(self.create_user_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status_error)

    def test_admin_post_user(self):
        self._create_user()

    def test_cannot_post_user_with_existing_username(self):
        self._create_user()
        self._create_user_failed()

    def test_customer_cannot_post_user(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.post(self.create_user_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_post_user_when_logout(self):
        self.client.logout()
        response = self.client.post(self.create_user_url, data=self.post_data,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
