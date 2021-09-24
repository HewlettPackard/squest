from django.urls import reverse

from service_catalog.models import Operation, Service
from tests.test_service_catalog.base import BaseTest


class ServiceDeleteTestCase(BaseTest):

    def setUp(self):
        super(ServiceDeleteTestCase, self).setUp()
        args = {
            "service_id": self.service_test.id
        }
        self.url = reverse('service_catalog:delete_service', kwargs=args)

    def test_delete_service(self):
        number_service_before = Service.objects.all().count()
        response = self.client.post(self.url)
        self.assertEquals(302, response.status_code)
        self.assertEquals(number_service_before - 1,
                          Service.objects.all().count())

    def test_standard_user_cannot_delete_service(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        number_service_before = Service.objects.all().count()
        response = self.client.post(self.url)
        self.assertEquals(302, response.status_code)
        self.assertEquals(number_service_before,
                          Service.objects.all().count())
