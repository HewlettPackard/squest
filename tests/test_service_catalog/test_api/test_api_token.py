from rest_framework import status
from rest_framework.reverse import reverse
from profiles.models import Token
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI
from django.utils import timezone


class TestAPIToken(BaseTestRequestAPI):

    def setUp(self):
        super(TestAPIToken, self).setUp()
        self.url = reverse('api_towerserver_list_create')
        self.api_token = Token.objects.create(user=self.superuser)
        self.api_token.save()
        self.api_token_user = Token.objects.create(user=self.standard_user)
        self.header = {'HTTP_AUTHORIZATION': f"Bearer {self.api_token.key}"}
        self.header_user = {'HTTP_AUTHORIZATION': f"Bearer {self.api_token_user.key}"}
        self.client.logout()

    def test_token_admin(self):
        response = self.client.get(self.url, format='json', **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_user_on_an_admin_page(self):
        response = self.client.get(self.url, format='json', **self.header_user)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_without_token(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_expired_token(self):
        expiration_date = timezone.now() - timezone.timedelta(days=2)
        self.api_token.refresh_from_db()
        self.api_token.expires = expiration_date
        self.api_token.save()
        response = self.client.get(self.url, format='json', **self.header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
