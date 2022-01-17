from django.urls import reverse
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestAdminSupportViews(BaseTestRequest):

    def setUp(self):
        super(TestAdminSupportViews, self).setUp()
        self.url = reverse('service_catalog:support_list')

    def test_get_support_list(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data), 2)

    def test_customer_can_list_his_support(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data), 1)
        self.assertEqual(response.context["table"].data.data.first(), self.support_test)

        self.client.force_login(user=self.standard_user_2)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data), 1)
        self.assertEqual(response.context["table"].data.data.first(), self.support_test2)

    def test_cannot_get_support_list_when_logout(self):
        self.client.logout()
        url = reverse('service_catalog:support_list')
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
