from django.urls import reverse
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestAdminSupportViews(BaseTestRequest):

    def setUp(self):
        super(TestAdminSupportViews, self).setUp()

    def test_get_support_list(self):
        url = reverse('service_catalog:support_list')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data), 1)

    def test_cannot_get_support_list_when_logout(self):
        self.client.logout()
        url = reverse('service_catalog:support_list')
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
