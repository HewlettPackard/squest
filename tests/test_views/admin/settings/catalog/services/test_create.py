from django.urls import reverse

from service_catalog.models import Operation, Service
from tests.base import BaseTest


class ServiceCreateTestCase(BaseTest):

    def setUp(self):
        super(ServiceCreateTestCase, self).setUp()
        self.url = reverse('service_catalog:create_service')

    def test_create_service(self):
        data = {
            "name": "new_service",
            "description": "a new service",
            "job_template": self.job_template_test.name,
        }
        number_service_before = Service.objects.all().count()
        response = self.client.post(self.url, data=data)
        self.assertEquals(302, response.status_code)
        self.assertEquals(number_service_before + 1,
                          Service.objects.all().count())
