from copy import copy

from django.urls import reverse

from resource_tracker.models import Resource, ResourceAttribute
from resource_tracker.tests.base_test_resource_tracker import BaseTestResourceTracker


class TestResourceGroupResourceViews(BaseTestResourceTracker):

    def setUp(self):
        super(TestResourceGroupResourceViews, self).setUp()

    def test_resource_group_resource_list(self):
        arg = {
            "resource_group_id": self.rg_physical_servers.id
        }
        url = reverse('resource_tracker:resource_group_resource_list', kwargs=arg)
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)
        self.assertTrue("resource_group" in response.context)
        self.assertTrue("list_attribute_name" in response.context)

    def test_resource_group_resource_delete(self):
        server_to_delete = Resource.objects.get(name="server-1")
        arg = {
            "resource_group_id": self.rg_physical_servers.id,
            "resource_id": server_to_delete.id
        }

        # test GET
        url = reverse('resource_tracker:resource_group_resource_delete', kwargs=arg)
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)

        # test POST
        attribute_id = copy(server_to_delete.id)
        self.assertTrue(Resource.objects.filter(id=attribute_id).exists())
        response = self.client.post(url)
        self.assertEquals(302, response.status_code)
        self.assertFalse(Resource.objects.filter(id=attribute_id).exists())

    def test_resource_group_resource_create_empty(self):
        arg = {
            "resource_group_id": self.rg_physical_servers.id
        }
        url = reverse('resource_tracker:resource_group_resource_create', kwargs=arg)

        # test GET
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)

        # test POST
        data = {
            "name": "new_resource",
            "CPU": "",
            "Memory": 12
        }
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.assertTrue(Resource.objects.filter(name="new_resource",
                                                resource_group=self.rg_physical_servers).exists())
        target_resource = Resource.objects.get(name="new_resource",
                                               resource_group=self.rg_physical_servers)
        self.assertEquals(2, len(target_resource.attributes.all()))

    def test_resource_group_resource_create(self):
        arg = {
            "resource_group_id": self.rg_physical_servers.id
        }
        url = reverse('resource_tracker:resource_group_resource_create', kwargs=arg)

        # test GET
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)

        # test POST
        data = {
            "name": "new_resource",
            "CPU": 12,
            "Memory": 12
        }
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.assertTrue(Resource.objects.filter(name="new_resource",
                                                resource_group=self.rg_physical_servers).exists())
        target_resource = Resource.objects.get(name="new_resource",
                                               resource_group=self.rg_physical_servers)
        self.assertEquals(2, len(target_resource.attributes.all()))

    def test_resource_group_resource_edit(self):
        resource_to_edit = Resource.objects.get(name="server-1",
                                                resource_group=self.rg_physical_servers)
        arg = {
            "resource_group_id": self.rg_physical_servers.id,
            "resource_id": resource_to_edit.id
        }
        url = reverse('resource_tracker:resource_group_resource_edit', kwargs=arg)

        # test GET
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)

        # test POST
        data = {
            "name": "updated_name",
            "CPU": 1,
            "Memory": 2
        }
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        resource_to_edit.refresh_from_db()
        self.assertEquals(resource_to_edit.name, "updated_name")

        resource_attribute_cpu = ResourceAttribute.objects.get(resource=resource_to_edit, attribute_type=self.rg_physical_servers_cpu_attribute)
        self.assertEquals(resource_attribute_cpu.value, 1)

        resource_attribute_memory = ResourceAttribute.objects.get(resource=resource_to_edit,
                                                                  attribute_type=self.rg_physical_servers_memory_attribute)
        self.assertEquals(resource_attribute_memory.value, 2)
