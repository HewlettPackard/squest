import copy

from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker.models import Resource
from service_catalog.models import Instance
from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestResourceUpdate(BaseTestAPI):

    def setUp(self):
        super(TestResourceUpdate, self).setUp()
        self.resource_to_update = Resource.objects.get(name="server-0")
        self.url = reverse('api_resource_retrieve_delete',  args=[self.rg_physical_servers.id,
                                                                  self.resource_to_update.id])

    def test_update_resource(self):
        data = {
            "id": self.resource_to_update.id,
            "name": "server-0-new-name",
            "service_catalog_instance": None,
            "attributes": [
                {
                    "name": "CPU",
                    "value": 1
                },
                {
                    "name": "Memory",
                    "value": 2
                }
            ],
            "text_attributes": [
                {
                    "name": "Description",
                    "value": "new-description"
                },
                {
                    "name": "Another text",
                    "value": "new-description-2"
                }
            ]
        }

        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertTrue("id" in response_json)
        self.assertTrue("name" in response_json)
        self.assertEqual("server-0-new-name", response_json["name"])
        self.assertTrue("service_catalog_instance" in response_json)
        self.assertTrue("attributes" in response_json)
        self.assertTrue("text_attributes" in response_json)

        self.resource_to_update.refresh_from_db()
        self.assertEqual(self.resource_to_update.name, "server-0-new-name")

        self.assertEqual(1, self.resource_to_update.attributes
                         .get(attribute_type=self.rg_physical_servers_cpu_attribute).value)
        self.assertEqual(2, self.resource_to_update.attributes
                         .get(attribute_type=self.rg_physical_servers_memory_attribute).value)
        self.assertEqual("new-description", self.resource_to_update.text_attributes
                         .get(text_attribute_type=self.rg_physical_servers_description).value)
        self.assertEqual("new-description-2", self.resource_to_update.text_attributes
                         .get(text_attribute_type=self.rg_physical_servers_text).value)

    def test_update_resource_missing_attribute(self):
        """
        Current behavior is the same as a "patch". If an attribute is missing we keep the previous value
        """
        data = {
            "id": self.resource_to_update.id,
            "name": "server-0-new-name",
            "service_catalog_instance": None,
            "attributes": [
                {
                    "name": "CPU",
                    "value": 1
                }

            ],
            "text_attributes": [
                {
                    "name": "Description",
                    "value": "new-description"
                }
            ]
        }
        previous_memory = self.resource_to_update.attributes.\
            get(attribute_type=self.rg_physical_servers_memory_attribute).value
        previous_description = copy.copy(self.resource_to_update.text_attributes.
                                         get(text_attribute_type=self.rg_physical_servers_text).value)

        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.resource_to_update.refresh_from_db()
        self.assertEqual(self.resource_to_update.name, "server-0-new-name")

        self.assertEqual(1, self.resource_to_update.attributes
                         .get(attribute_type=self.rg_physical_servers_cpu_attribute).value)
        # we should have the same memory value
        self.assertEqual(previous_memory, self.resource_to_update.attributes
                         .get(attribute_type=self.rg_physical_servers_memory_attribute).value)
        # and same description
        self.assertEqual(previous_description, self.resource_to_update.text_attributes.
                         get(text_attribute_type=self.rg_physical_servers_text).value)

    def test_update_wrong_attribute_name(self):
        data = {
            "id": self.resource_to_update.id,
            "name": "server-0-new-name",
            "service_catalog_instance": None,
            "attributes": [
                {
                    "name": "non_exist",
                    "value": 1
                }

            ],
            "text_attributes": [
                {
                    "name": "Description",
                    "value": "new-description"
                }
            ]
        }
        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_wrong_text_attribute_name(self):
        data = {
            "id": self.resource_to_update.id,
            "name": "server-0-new-name",
            "service_catalog_instance": None,
            "attributes": [
                {
                    "name": "CPU",
                    "value": 1
                }

            ],
            "text_attributes": [
                {
                    "name": "non_exist",
                    "value": "new-description"
                }
            ]
        }
        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_resource_set_instance(self):
        test_instance = Instance.objects.create(name="test_instance_1", service=None,
                                                     spoc=self.standard_user)
        data = {
            "id": self.resource_to_update.id,
            "name": "server-0-new-name",
            "service_catalog_instance": test_instance.id,
            "attributes": [
            ],
            "text_attributes": [

            ]
        }
        self.assertEqual(self.resource_to_update.service_catalog_instance, None)
        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.resource_to_update.refresh_from_db()
        self.assertEqual(self.resource_to_update.service_catalog_instance.id, test_instance.id)
