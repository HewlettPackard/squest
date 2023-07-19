from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestApiUserDelete(BaseTestRequest):

    def setUp(self):
        super(TestApiUserDelete, self).setUp()
        self.user_to_delete_id = self.standard_user.id
        self.kwargs = {
            'pk': self.user_to_delete_id
        }
        self.delete_user_url = reverse('api_user_details', kwargs=self.kwargs)

    def test_admin_delete_user(self):
        user_count = User.objects.count()
        response = self.client.delete(self.delete_user_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(user_count - 1, User.objects.count())
        self.assertFalse(User.objects.filter(id=self.user_to_delete_id).exists())

    def test_customer_cannot_delete_user(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.delete(self.delete_user_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_delete_user_when_logout(self):
        self.client.logout()
        response = self.client.delete(self.delete_user_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
