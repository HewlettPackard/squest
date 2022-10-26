from django.urls import reverse

from resource_tracker.models import ResourceGroup, ResourcePool
from tests.test_resource_tracker.base_test_resource_tracker import BaseTestResourceTracker


class TestResourceGraphViews(BaseTestResourceTracker):
    def setUp(self):
        super(TestResourceGraphViews, self).setUp()
        self.rg_test_without_tag = ResourceGroup.objects.create(name="without_tag")
        self.rp_test_without_tag = ResourcePool.objects.create(name="without_tag")
        self.rp_test = ResourcePool.objects.create(name="test")
        self.rp_test.tags.add("test1")
        self.rp_test.tags.add("test2")
        self.rp_vcenter.tags.add("test1")
        self.rp_ocp_workers.tags.add("test2")
        self.rg_physical_servers.tags.add("test1")
        self.rg_ocp_workers.tags.add("test2")
        self.rg_ocp_projects.tags.add("test1")
        self.rg_ocp_projects.tags.add("test2")

    def test_get_resource_tracker_graph(self):
        url = reverse('resource_tracker:resource_tracker_graph')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context['resource_pools'].count(), ResourcePool.objects.count())
        self.assertEqual(response.context['resource_groups'].count(), ResourceGroup.objects.count())

    def test_get_resource_tracker_graph_filter_type_and(self):
        url = reverse('resource_tracker:resource_tracker_graph') + "?tag=test1&tag=test2&tag_filter_type=AND"
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context['resource_pools'].count(), 1)
        self.assertEqual(response.context['resource_groups'].count(), 1)

    def test_get_resource_tracker_graph_filter_type_or(self):
        url = reverse('resource_tracker:resource_tracker_graph') + "?tag=test1&tag=test2&tag_filter_type=OR"
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context['resource_pools'].count(), 3)
        self.assertEqual(response.context['resource_groups'].count(), 3)


    def test_customer_cannot_get_resource_tracker_graph(self):
        self.client.logout()
        self.client.login(username=self.standard_user.username, password=self.common_password)
        url = reverse('resource_tracker:resource_tracker_graph')
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)

    def test_cannot_get_resource_tracker_graph_logout(self):
        self.client.logout()
        url = reverse('resource_tracker:resource_tracker_graph')
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
