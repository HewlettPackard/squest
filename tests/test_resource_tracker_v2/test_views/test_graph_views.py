from django.urls import reverse

from resource_tracker_v2.models import ResourceGroup
from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2


class TestGraphViews(BaseTestResourceTrackerV2):
    def setUp(self):
        super(TestGraphViews, self).setUp()
        self.rg_test_without_tag = ResourceGroup.objects.create(name="without_tag")
        self.cluster.tags.add("tag1")
        self.single_vms.tags.add("tag2")
        self.ocp_projects.tags.add("tag1")
        self.ocp_projects.tags.add("tag2")

    def test_get_resource_tracker_graph(self):
        url = reverse('resource_tracker_v2:resource_tracker_graph')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context['resource_groups'].count(), ResourceGroup.objects.count())

    def test_get_resource_tracker_graph_filter_type_and(self):
        url = reverse('resource_tracker_v2:resource_tracker_graph') + "?tag=tag1&tag=tag2&tag_filter_type=AND"
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context['resource_groups'].count(), 1)

    def test_get_resource_tracker_graph_filter_type_or(self):
        url = reverse('resource_tracker_v2:resource_tracker_graph') + "?tag=tag1&tag=tag2&tag_filter_type=OR"
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context['resource_groups'].count(), 3)

    def test_customer_cannot_get_resource_tracker_graph(self):
        self.client.logout()
        self.client.login(username=self.standard_user.username, password=self.common_password)
        url = reverse('resource_tracker_v2:resource_tracker_graph')
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

    def test_cannot_get_resource_tracker_graph_logout(self):
        self.client.logout()
        url = reverse('resource_tracker_v2:resource_tracker_graph')
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
