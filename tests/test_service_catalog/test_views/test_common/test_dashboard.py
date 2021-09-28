from django.urls import reverse
from tests.test_resource_tracker.base_test_resource_tracker import BaseTestResourceTracker


class TestDashboard(BaseTestResourceTracker):

    def test_admin_get_dashboard(self):
        expected_context_list = ['total_request', 'total_instance', 'total_support_opened',
                                 'total_user_without_billing_groups', 'total_user', 'pie_charts', 'chart_resource_pool']
        response = self.client.get(reverse('service_catalog:dashboards'))
        self.assertEquals(200, response.status_code)
        for expected_context in expected_context_list:
            self.assertIn(expected_context, response.context)

    def test_customer_get_dashboard(self):
        self.client.login(username=self.standard_user.username, password=self.common_password)
        not_expected_context_list = ['total_support_opened', 'total_user_without_billing_groups', 'total_user',
                                     'pie_charts', 'chart_resource_pool']
        expected_context_list = ['total_request', 'total_instance', 'total_request_need_info']
        response = self.client.get(reverse('service_catalog:dashboards'))
        self.assertEquals(200, response.status_code)
        for expected_context in expected_context_list:
            self.assertIn(expected_context, response.context)
        for not_expected_context in not_expected_context_list:
            self.assertNotIn(not_expected_context, response.context)

    def test_cannot_get_dashboard_when_logout(self):
        self.client.logout()
        response = self.client.get(reverse('service_catalog:dashboards'))
        self.assertEquals(302, response.status_code)

    def test_get_home(self):
        response = self.client.get(reverse('service_catalog:home'))
        self.assertEquals(200, response.status_code)

    def test_cannot_get_home_when_logout(self):
        self.client.logout()
        response = self.client.get(reverse('service_catalog:home'))
        self.assertEquals(302, response.status_code)
