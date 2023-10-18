from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class TestMonitoring(TestCase):

    def test_can_get_swagger_view(self):
        url = reverse('schema-swagger-ui') + "?format=openapi"
        testing_user = User.objects.create_user('stan1234', 'standard_user@hpe.com', 'password')
        self.client.force_login(testing_user)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_cannot_get_swagger_view_when_logout(self):
        url = reverse('schema-swagger-ui') + "?format=openapi"
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
