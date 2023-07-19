from django.urls import reverse

from service_catalog.models import Service
from tests.test_service_catalog.base import BaseTest


class ServiceDeleteTestCase(BaseTest):

    def setUp(self):
        super(ServiceDeleteTestCase, self).setUp()
        args = {
            "pk": self.service_test.id
        }
        self.url = reverse('service_catalog:service_delete', kwargs=args)

    def test_delete_service(self):
        number_service_before = Service.objects.all().count()
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(self.url)
        self.assertEqual(302, response.status_code)
        self.assertEqual(number_service_before - 1,
                          Service.objects.all().count())

    def test_standard_user_cannot_delete_service(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)
        number_service_before = Service.objects.all().count()
        response = self.client.post(self.url)
        self.assertEqual(403, response.status_code)
        self.assertEqual(number_service_before,
                          Service.objects.all().count())
