from django.urls import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestCustomerRequestList(BaseTestRequest):

    def setUp(self):
        super(TestCustomerRequestList, self).setUp()

    def test_user_can_list_his_requests(self):
        # fist user has one request
        url = reverse('service_catalog:request_list')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data), 1)
        self.client.logout()
        # second user has no request
        self.client.login(username=self.standard_user_2, password=self.common_password)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data), 0)

    def test_cannot_get_requests_list_when_logout(self):
        self.client.logout()
        url = reverse('service_catalog:request_list')
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
