import copy

from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker.models import Resource
from service_catalog.models import Instance
from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestResourcePatch(BaseTestAPI):

    def setUp(self):
        super(TestResourcePatch, self).setUp()
        self.instance = Instance.objects.create(name="test_instance")
        self.resource_to_patch = Resource.objects.get(name="server-0")
        self.url = reverse('api_resource_retrieve_delete',  args=[self.rg_physical_servers.id,
                                                                  self.resource_to_patch.id])

    def test_patch_resource(self):
        old_name = self.resource_to_patch.name
        old_instance = self.resource_to_patch.service_catalog_instance
        old_cpu_val = self.resource_to_patch.attributes.get(attribute_type=self.rg_physical_servers_cpu_attribute).value
        old_text_val = self.resource_to_patch.text_attributes.get(
            text_attribute_type=self.rg_physical_servers_text).value
        data = {
            "service_catalog_instance": self.instance.id,
            "attributes": [
                {
                    "name": "CPU",
                    "value": 1
                },
            ],
            "text_attributes": [
                {
                    "name": "Another text",
                    "value": "new-description-2"
                }
            ]
        }

        response = self.client.patch(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.resource_to_patch.refresh_from_db()
        self.assertEqual(self.resource_to_patch.name, old_name)
        self.assertNotEqual(
            self.resource_to_patch.attributes.get(attribute_type=self.rg_physical_servers_cpu_attribute).value,
            old_cpu_val)
        self.assertEqual(
            self.resource_to_patch.attributes.get(attribute_type=self.rg_physical_servers_cpu_attribute).value, 1)
        self.assertNotEqual(self.resource_to_patch.service_catalog_instance, old_instance)
        self.assertEqual(self.resource_to_patch.service_catalog_instance, self.instance)
        self.assertNotEqual(
            self.resource_to_patch.text_attributes.get(text_attribute_type=self.rg_physical_servers_text).value,
            old_text_val)
        self.assertEqual(
            self.resource_to_patch.text_attributes.get(text_attribute_type=self.rg_physical_servers_text).value,
            "new-description-2")

    def test_patch_resource_missing_attributes(self):
        old_text_val = self.resource_to_patch.text_attributes.get(
            text_attribute_type=self.rg_physical_servers_text).value
        old_attribute_count = self.resource_to_patch.attributes.count()
        old_text_attribute_count = self.resource_to_patch.text_attributes.count()
        data = {
            "text_attributes": [
                {
                    "name": "Another text",
                    "value": "new-description-2"
                }
            ]
        }
        response = self.client.patch(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.resource_to_patch.refresh_from_db()
        self.assertEqual(self.resource_to_patch.attributes.count(), old_attribute_count)
        self.assertEqual(self.resource_to_patch.text_attributes.count(), old_text_attribute_count)
        self.assertNotEqual(
            self.resource_to_patch.text_attributes.get(text_attribute_type=self.rg_physical_servers_text).value,
            old_text_val)
        self.assertEqual(
            self.resource_to_patch.text_attributes.get(text_attribute_type=self.rg_physical_servers_text).value,
            "new-description-2")

    def test_patch_resource_missing_text_attributes(self):
        old_cpu_val = self.resource_to_patch.attributes.get(attribute_type=self.rg_physical_servers_cpu_attribute).value
        old_attribute_count = self.resource_to_patch.attributes.count()
        old_text_attribute_count = self.resource_to_patch.text_attributes.count()
        data = {
            "attributes": [
                {
                    "name": "CPU",
                    "value": 1
                },
            ]
        }
        response = self.client.patch(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.resource_to_patch.refresh_from_db()
        self.assertEqual(self.resource_to_patch.attributes.count(), old_attribute_count)
        self.assertEqual(self.resource_to_patch.text_attributes.count(), old_text_attribute_count)
        self.assertNotEqual(
            self.resource_to_patch.attributes.get(attribute_type=self.rg_physical_servers_cpu_attribute).value,
            old_cpu_val)
        self.assertEqual(
            self.resource_to_patch.attributes.get(attribute_type=self.rg_physical_servers_cpu_attribute).value, 1)

    def test_patch_wrong_attribute_name(self):
        data = {
            "attributes": [
                {
                    "name": "non_exist",
                    "value": 1
                }

            ],
        }
        response = self.client.patch(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_wrong_text_attribute_name(self):
        data = {
            "text_attributes": [
                {
                    "name": "non_exist",
                    "value": "new-description"
                }
            ]
        }
        response = self.client.patch(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
