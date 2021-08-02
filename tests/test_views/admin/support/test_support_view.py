import json

from django.urls import reverse

from service_catalog.models import Support
from tests.base_test_request import BaseTestRequest


class TestAdminSupportViews(BaseTestRequest):

    def setUp(self):
        super(TestAdminSupportViews, self).setUp()

    def test_get_support_list(self):
        url = reverse('service_catalog:admin_support_list')
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)
        self.assertTrue("supports" in response.context)
        self.assertEquals(len(response.context["supports"].qs), 1)
