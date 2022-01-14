from django.urls import reverse
from tests.test_resource_tracker.base_test_resource_tracker import BaseTestResourceTracker


class TestHome(BaseTestResourceTracker):

    def setUp(self):
        super(TestHome, self).setUp()
        self.url = reverse('service_catalog:home')

    def test_admin_get_home(self):
        expected_context_list = ['total_request', 'total_instance', 'total_support_opened',
                                 'total_user_without_billing_groups', 'total_user']
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        for expected_context in expected_context_list:
            self.assertIn(expected_context, response.context)

    def test_customer_get_home(self):
        self.client.login(username=self.standard_user.username, password=self.common_password)
        not_expected_context_list = ['total_support_opened', 'total_user_without_billing_groups', 'total_user',
                                     'pie_charts']
        expected_context_list = ['total_request', 'total_instance', 'total_request_need_info']
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        for expected_context in expected_context_list:
            self.assertIn(expected_context, response.context)
        for not_expected_context in not_expected_context_list:
            self.assertNotIn(not_expected_context, response.context)

    def test_cannot_get_home_when_logout(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(302, response.status_code)

    def test_get_home(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
