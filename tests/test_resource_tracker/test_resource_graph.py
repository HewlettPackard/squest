from django.urls import reverse
from tests.test_resource_tracker.base_test_resource_tracker import BaseTestResourceTracker


class TestResourceGraphViews(BaseTestResourceTracker):

    def test_get_resource_tracker_graph(self):
        url = reverse('resource_tracker:resource_tracker_graph')
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)

    def test_customer_cannot_get_resource_tracker_graph(self):
        self.client.logout()
        self.client.login(username=self.standard_user.username, password=self.common_password)
        url = reverse('resource_tracker:resource_tracker_graph')
        response = self.client.get(url)
        self.assertEquals(302, response.status_code)

    def test_cannot_get_resource_tracker_graph_logout(self):
        self.client.logout()
        url = reverse('resource_tracker:resource_tracker_graph')
        response = self.client.get(url)
        self.assertEquals(302, response.status_code)
