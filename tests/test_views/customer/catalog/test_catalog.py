from django.urls import reverse

from service_catalog.models import Request
from tests.base_test_request import BaseTestRequest


class TestCustomerCatalogViews(BaseTestRequest):

    def setUp(self):
        super(TestCustomerCatalogViews, self).setUp()
        self.client.login(username=self.standard_user, password=self.common_password)

    def test_customer_list_service(self):
        url = reverse('service_catalog:service_list')
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)
        self.assertTrue("services" in response.context)
        self.assertEquals(len(response.context["services"]), 2)

    def test_customer_cannot_manage_service(self):
        url = reverse('service_catalog:manage_services')
        response = self.client.get(url)
        self.assertEquals(403, response.status_code)

    def test_customer_service_request(self):
        args = {
            "service_id": self.service_test.id
        }
        url = reverse('service_catalog:customer_service_request', kwargs=args)

        data = {
            "instance_name": "instance_1",
            "text_variable": "text_value_1",
            "multiplechoice_variable": "text_value_2"
        }
        number_request_before = Request.objects.all().count()
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.assertEquals(number_request_before + 1, Request.objects.all().count())
