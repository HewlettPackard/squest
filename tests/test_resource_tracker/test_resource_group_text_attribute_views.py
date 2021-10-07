from copy import copy

from django.urls import reverse

from resource_tracker.models import ResourceGroupTextAttributeDefinition, Resource
from tests.test_resource_tracker.base_test_resource_tracker import BaseTestResourceTracker


class TestResourceGroupTextAttributeViews(BaseTestResourceTracker):

    def setUp(self):
        super(TestResourceGroupTextAttributeViews, self).setUp()

    def test_resource_group_text_attribute_create(self):
        args = {
            "resource_group_id": self.rg_physical_servers.id,
        }
        url = reverse('resource_tracker:resource_group_text_attribute_create', kwargs=args)

        # test GET
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertTrue("resource_group" in response.context)

        new_name = "new_text_attribute_name"
        data = {
            "name": new_name
        }
        number_text_attribute_before = ResourceGroupTextAttributeDefinition.objects.all().count()
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(number_text_attribute_before + 1, ResourceGroupTextAttributeDefinition.objects.all().count())
        self.assertTrue(ResourceGroupTextAttributeDefinition.objects.filter(name="new_text_attribute_name",
                                                                            resource_group_definition=self.rg_physical_servers).exists())

        # test POST
        new_name = "new_text_attribute_name_2"
        data = {
            "name": new_name,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertTrue(ResourceGroupTextAttributeDefinition.objects.filter(name="new_text_attribute_name_2",
                                                                            resource_group_definition=self.rg_physical_servers).exists())
        # test POST with already exist attribute
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(f"Attribute {new_name} already exist in {self.rg_physical_servers.name}",
                          response.context['form'].errors['name'][0])

    def test_resource_group_text_attribute_create_logout(self):
        self.client.logout()
        args = {
            "resource_group_id": self.rg_physical_servers.id,
        }
        url = reverse('resource_tracker:resource_group_text_attribute_create', kwargs=args)

        # test GET
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)

    def test_resource_group_text_attribute_edit(self):
        args = {
            "resource_group_id": self.rg_physical_servers.id,
            "attribute_id": self.rg_physical_servers_description.id
        }
        url = reverse('resource_tracker:resource_group_text_attribute_edit', kwargs=args)

        # test GET
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        new_name = "new_text_attribute_name"
        data = {
            "name": new_name
        }
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.rg_physical_servers_description.refresh_from_db()
        self.assertEqual(self.rg_physical_servers_description.name, "new_text_attribute_name")

    def test_cannot_edit_resource_group_text_attribute_when_logout(self):
        self.client.logout()
        args = {
            "resource_group_id": self.rg_physical_servers.id,
            "attribute_id": self.rg_physical_servers_description.id
        }
        url = reverse('resource_tracker:resource_group_text_attribute_edit', kwargs=args)

        # test GET
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)

    def test_resource_group_text_attribute_edit_existing_name(self):
        args = {
            "resource_group_id": self.rg_physical_servers.id,
            "attribute_id": self.rg_physical_servers_description.id
        }
        url = reverse('resource_tracker:resource_group_text_attribute_edit', kwargs=args)

        # test GET
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        new_name = self.rg_physical_servers_text.name
        data = {
            "name": new_name
        }
        old_name = self.rg_physical_servers_description.name
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.rg_physical_servers_description.refresh_from_db()
        self.assertEqual(self.rg_physical_servers_description.name, old_name)

    def test_resource_group_text_attribute_edit_same_name(self):
        args = {
            "resource_group_id": self.rg_physical_servers.id,
            "attribute_id": self.rg_physical_servers_description.id
        }
        url = reverse('resource_tracker:resource_group_text_attribute_edit', kwargs=args)

        # test GET
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        # test POST without producer or consumer
        new_name = self.rg_physical_servers_text.name
        data = {
            "name": self.rg_physical_servers_description.name,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)

    def test_resource_group_text_attribute_delete(self):
        args = {
            "resource_group_id": self.rg_physical_servers.id,
            "attribute_id": self.rg_physical_servers_description.id
        }
        url = reverse('resource_tracker:resource_group_text_attribute_delete', kwargs=args)

        # test GET
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        # test POST
        attribute_id = copy(self.rg_physical_servers_description.id)
        self.assertTrue(ResourceGroupTextAttributeDefinition.objects.filter(id=attribute_id).exists())
        response = self.client.post(url)
        self.assertEqual(302, response.status_code)
        self.assertFalse(ResourceGroupTextAttributeDefinition.objects.filter(id=attribute_id).exists())

    def test_cannot_delete_resource_group_text_attribute_when_logout(self):
        self.client.logout()
        args = {
            "resource_group_id": self.rg_physical_servers.id,
            "attribute_id": self.rg_physical_servers_description.id
        }
        url = reverse('resource_tracker:resource_group_text_attribute_delete', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)

    def test_create_resource_after_adding_text_attributes(self):
        args = {
            "resource_group_id": self.rg_physical_servers.id,
        }
        url = reverse('resource_tracker:resource_group_text_attribute_create', kwargs=args)

        # test GET
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertTrue("resource_group" in response.context)

        new_name = "new_text_attribute_name"
        data = {
            "name": new_name
        }
        number_text_attribute_before = ResourceGroupTextAttributeDefinition.objects.all().count()
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(number_text_attribute_before + 1, ResourceGroupTextAttributeDefinition.objects.all().count())
        self.assertTrue(ResourceGroupTextAttributeDefinition.objects.filter(name="new_text_attribute_name",
                                                                            resource_group_definition=self.rg_physical_servers).exists())

        # test POST with producer
        new_name = "new_text_attribute_name_2"
        data = {
            "name": new_name,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertTrue(ResourceGroupTextAttributeDefinition.objects.filter(name="new_text_attribute_name_2",
                                                                            resource_group_definition=self.rg_physical_servers).exists())


        url = reverse('resource_tracker:resource_group_resource_create', kwargs=args)
        data = {
            "name": "new resource"
        }
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)

        self.assertIsInstance(Resource.objects.get(name="new resource"), Resource)

        url = reverse('resource_tracker:resource_group_resource_list', kwargs=args)
        response = self.client.get(url, data=data)
        self.assertEqual(200, response.status_code)
