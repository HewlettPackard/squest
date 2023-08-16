from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestApiUserList(BaseTestRequestAPI):

    def setUp(self):
        super(TestApiUserList, self).setUp()
        self.get_user_list_url = reverse('api_user_list_create')

    def test_get_all_users(self):
        response = self.client.get(self.get_user_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], User.objects.count())

    def test_customer_cannot_get_user_list(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.get_user_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_get_user_list_when_logout(self):
        self.client.logout()
        response = self.client.get(self.get_user_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
