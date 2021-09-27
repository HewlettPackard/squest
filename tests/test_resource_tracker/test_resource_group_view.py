from copy import copy

from django.urls import reverse

from resource_tracker.models import ResourceGroup, Resource, ResourceAttribute, ResourceTextAttribute
from tests.test_resource_tracker.base_test_resource_tracker import BaseTestResourceTracker


class TestResourceGroupViews(BaseTestResourceTracker):

    def setUp(self):
        super(TestResourceGroupViews, self).setUp()

    def test_resource_group_list(self):
        url = reverse('resource_tracker:resource_group_list')
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)
        self.assertTrue("resource_groups" in response.context)

    def test_cannot_get_resource_group_list_when_logout(self):
        self.client.logout()
        url = reverse('resource_tracker:resource_group_list')
        response = self.client.get(url)
        self.assertEquals(302, response.status_code)

    def test_resource_group_create(self):
        url = reverse('resource_tracker:resource_group_create')
        data = {
            "name": "new_resource_group",
        }
        number_rp_before = ResourceGroup.objects.all().count()
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.assertEquals(number_rp_before + 1, ResourceGroup.objects.all().count())
        self.assertTrue(ResourceGroup.objects.filter(name="new_resource_group").exists())

    def test_resource_group_edit(self):
        args = {
            "resource_group_id": self.rg_physical_servers.id,
        }
        url = reverse('resource_tracker:resource_group_edit', kwargs=args)

        new_name = "new_group_url"
        data = {
            "name": new_name,
        }
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.rg_physical_servers.refresh_from_db()
        self.assertEquals(self.rg_physical_servers.name, new_name)

    def test_resource_group_delete(self):
        id_to_delete = copy(self.rg_physical_servers.id)
        args = {
            'resource_group_id': self.rg_physical_servers.id,
        }
        list_resource_id_to_be_delete = list()
        list_attribute_id_to_be_delete = list()
        list_text_attribute_id_to_be_delete = list()
        for resource in self.rg_physical_servers.resources.all():
            list_resource_id_to_be_delete.append(copy(resource.id))
            for attribute in resource.attributes.all():
                list_attribute_id_to_be_delete.append(copy(attribute.id))
            for attribute in resource.text_attributes.all():
                list_text_attribute_id_to_be_delete.append(copy(attribute.id))
        url = reverse('resource_tracker:resource_group_delete', kwargs=args)
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)
        response = self.client.post(url)
        self.assertEquals(302, response.status_code)
        # check that the resource group has been deleted
        self.assertFalse(ResourceGroup.objects.filter(id=id_to_delete).exists())
        # check that all resource instances have been deleted
        for resource_id in list_resource_id_to_be_delete:
            self.assertFalse(Resource.objects.filter(id=resource_id).exists())
        # check that all attributes of instances have been deleted
        for attribute_id in list_attribute_id_to_be_delete:
            self.assertFalse(ResourceAttribute.objects.filter(id=attribute_id).exists())
        for attribute_id in list_text_attribute_id_to_be_delete:
            self.assertFalse(ResourceTextAttribute.objects.filter(id=attribute_id).exists())
