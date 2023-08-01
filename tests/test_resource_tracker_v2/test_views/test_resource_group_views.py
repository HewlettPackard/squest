from copy import copy

from django.urls import reverse

from resource_tracker_v2.models import ResourceGroup
from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2


class TestResourceGroupViews(BaseTestResourceTrackerV2):

    def setUp(self):
        super(TestResourceGroupViews, self).setUp()
        self.rg_test_without_tag = ResourceGroup.objects.create(name="without_tag")
        self.cluster.tags.add("tag1")
        self.single_vms.tags.add("tag2")
        self.ocp_projects.tags.add("tag1")
        self.ocp_projects.tags.add("tag2")

    def test_resource_group_list(self):
        response = self.client.get(reverse('resource_tracker_v2:resourcegroup_list'))
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data), ResourceGroup.objects.all().count())

    def test_resource_group_list_as_standard_user(self):
        self.client.force_login(self.standard_user)
        response = self.client.get(reverse('resource_tracker_v2:resourcegroup_list'))
        self.assertEqual(403, response.status_code)

    def test_resource_group_list_with_tag_and(self):
        response = self.client.get(reverse('resource_tracker_v2:resourcegroup_list') + "?tag=tag1&tag=tag2&tag_filter_type=AND")
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data), 1)

    def test_resource_group_list_with_tag_or(self):
        response = self.client.get(reverse('resource_tracker_v2:resourcegroup_list') + "?tag=tag1&tag=tag2&tag_filter_type=OR")
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data), 3)

    def test_resource_group_create(self):
        url = reverse('resource_tracker_v2:resourcegroup_create')
        data = {
            "name": "new_resource_group",
        }
        number_rp_before = ResourceGroup.objects.all().count()
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(number_rp_before + 1, ResourceGroup.objects.all().count())
        self.assertTrue(ResourceGroup.objects.filter(name="new_resource_group").exists())

    def test_resource_group_edit(self):
        args = {
            "pk": self.cluster.id,
        }
        url = reverse('resource_tracker_v2:resourcegroup_edit', kwargs=args)

        new_name = "new_group_url"
        data = {
            "name": new_name,
        }
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.cluster.refresh_from_db()
        self.assertEqual(self.cluster.name, new_name)

    def test_resource_group_delete(self):
        id_to_delete = copy(self.cluster.id)
        args = {
            'pk': self.cluster.id,
        }
        url = reverse('resource_tracker_v2:resourcegroup_delete', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url)
        self.assertEqual(302, response.status_code)
        # check that the resource group has been deleted
        self.assertFalse(ResourceGroup.objects.filter(id=id_to_delete).exists())
