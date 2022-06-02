from django.test import TestCase
from django.urls import reverse


class TestMonitoring(TestCase):

    def test_can_get_swagger_view(self):
        url = reverse('schema-swagger-ui') + "?format=openapi"
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
