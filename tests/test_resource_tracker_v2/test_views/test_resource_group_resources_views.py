from copy import copy

from django.urls import reverse

from resource_tracker_v2.models import Resource
from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2


class TestResourceGroupResourcesViews(BaseTestResourceTrackerV2):

    def setUp(self):
        super(TestResourceGroupResourcesViews, self).setUp()
        args = {
            "resource_group_id": self.ocp_projects.id
        }
        self.url_confirm = reverse('resource_tracker_v2:resourcegroup_resource_bulk_delete_confirm', kwargs=args)
        self.url_delete = reverse('resource_tracker_v2:resourcegroup_resource_bulk_delete', kwargs=args)

    def test_resource_group_resources_list(self):
        args = {
            "resource_group_id": self.ocp_projects.id
        }
        response = self.client.get(reverse('resource_tracker_v2:resourcegroup_resource_list', kwargs=args))
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data),
                         Resource.objects.filter(resource_group=self.ocp_projects).count())

    def test_resource_group_resources_create(self):
        args = {
            "resource_group_id": self.cluster.id
        }
        url = reverse('resource_tracker_v2:resourcegroup_resource_create', kwargs=args)

        # test GET
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        # test POST
        data = {
            "name": "new_resource",
            "resource_group": self.cluster.id,
            f"{self.core_attribute.name}": 10,
            f"{self.memory_attribute.name}": 20,
            "is_deleted_on_instance_deletion": True
        }
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertTrue(Resource.objects.filter(name="new_resource",
                                                resource_group=self.cluster).exists())
        target_resource = Resource.objects.get(name="new_resource",
                                               resource_group=self.cluster)
        self.assertEqual(10, target_resource.resource_attributes.
                         filter(attribute_definition=self.core_attribute).first().value)
        self.assertEqual(20, target_resource.resource_attributes.
                         filter(attribute_definition=self.memory_attribute).first().value)
        self.assertEqual(0, target_resource.resource_attributes.
                         filter(attribute_definition=self.three_par_attribute).first().value)

    def test_resource_group_resources_edit(self):
        args = {
            "resource_group_id": self.cluster.id,
            "resource_id": self.server1.id
        }
        url = reverse('resource_tracker_v2:resourcegroup_resource_edit', kwargs=args)

        # test GET
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        # test POST
        data = {
            "resource_group": self.cluster.id,
            "name": "new_resource",
            f"{self.core_attribute.name}": 1,
            f"{self.memory_attribute.name}": 2
        }
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)

        self.assertEqual(1, self.server1.resource_attributes.filter(
            attribute_definition=self.core_attribute).first().value)
        self.assertEqual(2, self.server1.resource_attributes.filter(
            attribute_definition=self.memory_attribute).first().value)
        self.assertEqual(0, self.server1.resource_attributes.filter(
            attribute_definition=self.three_par_attribute).first().value)

    def test_resource_group_resources_delete(self):
        args = {
            "resource_group_id": self.cluster.id,
            "resource_id": self.server1.id
        }
        url = reverse('resource_tracker_v2:resourcegroup_resource_delete', kwargs=args)

        # test GET
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        # test POST
        id_to_delete = copy(self.cluster.id)
        response = self.client.post(url)
        self.assertEqual(302, response.status_code)
        self.assertFalse(Resource.objects.filter(id=id_to_delete).exists())

    def test_admin_can_confirm_bulk_delete(self):
        resource_list_to_delete = [self.server1.id, self.server2.id]
        data = {"selection": resource_list_to_delete}

        response = self.client.post(self.url_confirm, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set([resource.id for resource in response.context['object_list']]),
            set(resource_list_to_delete)
        )

    def test_admin_get_message_on_confirm_bulk_delete_with_empty_data(self):
        response = self.client.post(self.url_confirm)
        self.assertEqual(response.status_code, 302)

    def test_admin_can_bulk_delete(self):
        resource_list_to_delete = [self.server1.id, self.server2.id]
        data = {"selection": resource_list_to_delete}
        response = self.client.post(self.url_delete, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Resource.objects.filter(id__in=resource_list_to_delete).count(), 0)
