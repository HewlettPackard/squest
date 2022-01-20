from copy import copy

from django.urls import reverse

from resource_tracker.models import Resource, ResourceAttribute, ResourceTextAttribute, ResourceGroupAttributeDefinition
from tests.test_resource_tracker.base_test_resource_tracker import BaseTestResourceTracker


class TestResourceGroupResourceViews(BaseTestResourceTracker):

    def setUp(self):
        super(TestResourceGroupResourceViews, self).setUp()

    def test_resource_group_resource_list(self):
        arg = {
            "resource_group_id": self.rg_physical_servers.id
        }
        columns = ['selection', 'name', 'CPU', 'Memory', 'Description', 'Another text', 'operations']
        url = reverse('resource_tracker:resource_group_resource_list', kwargs=arg)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertTrue("resource_group_id" in response.context)
        for column in columns:
            self.assertTrue(column in response.context['table'].columns.columns)
            self.assertTrue(column in response.context['table'].base_columns)
            self.assertTrue(column in response.context['table'].sequence)
            self.assertTrue(column in response.context['table'].Meta.fields)

    def test_cannot_get_resource_group_resource_list_when_logout(self):
        arg = {
            "resource_group_id": self.rg_physical_servers.id
        }
        url = reverse('resource_tracker:resource_group_resource_list', kwargs=arg)
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)

    def test_resource_group_resource_delete(self):
        server_to_delete = Resource.objects.get(name="server-1")
        arg = {
            "resource_group_id": self.rg_physical_servers.id,
            "resource_id": server_to_delete.id
        }

        # test GET
        url = reverse('resource_tracker:resource_group_resource_delete', kwargs=arg)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        # test POST
        attribute_id = copy(server_to_delete.id)
        self.assertTrue(Resource.objects.filter(id=attribute_id).exists())
        response = self.client.post(url)
        self.assertEqual(302, response.status_code)
        self.assertFalse(Resource.objects.filter(id=attribute_id).exists())

    def test_cannot_delete_resource_group_resource_when_logout(self):
        server_to_delete = Resource.objects.get(name="server-1")
        arg = {
            "resource_group_id": self.rg_physical_servers.id,
            "resource_id": server_to_delete.id
        }

        # test GET
        url = reverse('resource_tracker:resource_group_resource_delete', kwargs=arg)
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)

    def test_resource_group_resource_create_empty(self):
        arg = {
            "resource_group_id": self.rg_physical_servers.id
        }
        url = reverse('resource_tracker:resource_group_resource_create', kwargs=arg)

        # test GET
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        # test POST
        data = {
            "name": "new_resource",
            "CPU": "",
            "Memory": 12,
            "is_deleted_on_instance_deletion": True
        }
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertTrue(Resource.objects.filter(name="new_resource",
                                                resource_group=self.rg_physical_servers).exists())
        target_resource = Resource.objects.get(name="new_resource",
                                               resource_group=self.rg_physical_servers)
        self.assertEqual(2, len(target_resource.attributes.all()))

    def test_cannot_create_resource_group_resource_when_logout(self):
        self.client.logout()
        arg = {
            "resource_group_id": self.rg_physical_servers.id
        }
        url = reverse('resource_tracker:resource_group_resource_create', kwargs=arg)

        # test GET
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)

    def test_resource_group_resource_create_non_integer_value(self):
        arg = {
            "resource_group_id": self.rg_physical_servers.id
        }
        url = reverse('resource_tracker:resource_group_resource_create', kwargs=arg)

        # test GET
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        # test POST
        data = {
            "name": "new_resource",
            "CPU": "eee",
            "Memory": "ee"
        }
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(0, self.rg_physical_servers.resources.filter(name='new_resource').count())

    def test_resource_group_resource_create_negative_value(self):
        arg = {
            "resource_group_id": self.rg_physical_servers.id
        }
        url = reverse('resource_tracker:resource_group_resource_create', kwargs=arg)

        # test GET
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        # test POST
        data = {
            "name": "new_resource",
            "CPU": "0",
            "Memory": "-12"
        }
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(0, self.rg_physical_servers.resources.filter(name='new_resource').count())

    def test_resource_group_resource_create(self):
        arg = {
            "resource_group_id": self.rg_physical_servers.id
        }
        url = reverse('resource_tracker:resource_group_resource_create', kwargs=arg)

        # test GET
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        # test POST
        data = {
            "name": "new_resource",
            "CPU": 12,
            "Memory": 12,
            "Description": "text",
            "is_deleted_on_instance_deletion": True
        }
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertTrue(Resource.objects.filter(name="new_resource",
                                                resource_group=self.rg_physical_servers).exists())
        target_resource = Resource.objects.get(name="new_resource",
                                               resource_group=self.rg_physical_servers)
        self.assertEqual(2, len(target_resource.attributes.all()))

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
        self.assertEqual(200, response.status_code)

        # test POST
        data = {
            "name": "updated_name",
            "CPU": 1,
            "Memory": 2,
            "Description": "text modified",
            "is_deleted_on_instance_deletion": True
        }
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        resource_to_edit.refresh_from_db()
        self.assertEqual(resource_to_edit.name, "updated_name")

        resource_attribute_cpu = ResourceAttribute.objects.get(
            resource=resource_to_edit,
            attribute_type=self.rg_physical_servers_cpu_attribute
        )
        self.assertEqual(resource_attribute_cpu.value, 1)

        resource_attribute_memory = ResourceAttribute.objects.get(
            resource=resource_to_edit,
            attribute_type=self.rg_physical_servers_memory_attribute
        )
        self.assertEqual(resource_attribute_memory.value, 2)
        resource_text_attribute_description = ResourceTextAttribute.objects.get(
            resource=resource_to_edit,
            text_attribute_type=self.rg_physical_servers_description
        )
        self.assertEqual(resource_text_attribute_description.value, "text modified")

    def test_cannot_edit_resource_group_resource_when_logout(self):
        self.client.logout()
        resource_to_edit = Resource.objects.get(name="server-1",
                                                resource_group=self.rg_physical_servers)
        arg = {
            "resource_group_id": self.rg_physical_servers.id,
            "resource_id": resource_to_edit.id
        }
        url = reverse('resource_tracker:resource_group_resource_edit', kwargs=arg)

        # test GET
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)

    def test_delete_attribute_definition_from_resource_group(self):
        # create a resource in a resource group with an attribute
        worker_node_test = self.rg_ocp_workers.create_resource(name=f"worker-test")
        worker_node_test.set_attribute(self.rg_ocp_workers_vcpu_attribute, 16)
        worker_node_test.set_attribute(self.rg_ocp_workers_memory_attribute, 50)
        self.assertTrue(worker_node_test.attributes.filter(attribute_type__name="vCPU").exists())

        # we can reach the list of resource page
        arg = {
            "resource_group_id": self.rg_ocp_workers.id
        }
        url = reverse('resource_tracker:resource_group_resource_list', kwargs=arg)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        # delete the attribute from the resource group definition
        the_id = self.rg_ocp_workers_vcpu_attribute.id
        self.rg_ocp_workers_vcpu_attribute.delete()
        self.assertTrue(ResourceGroupAttributeDefinition.objects.get(id=self.rg_ocp_workers_memory_attribute.id))
        self.assertEqual(0, ResourceAttribute.objects.filter(attribute_type_id=the_id).count())
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertFalse(worker_node_test.attributes.filter(attribute_type__name="vCPU").exists())
