from django.urls import reverse

from service_catalog.models import Service
from tests.test_service_catalog.base import BaseTest


class ServiceListViewsTest(BaseTest):

    def setUp(self):
        super(ServiceListViewsTest, self).setUp()
        self.url = reverse('service_catalog:service_list')

    def test_get_list(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data), Service.objects.count())
