from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker_v2.api.serializers.resource_serializer import ResourceSerializer
from resource_tracker_v2.models import Transformer, Resource
from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2API


class TestResourceAPIView(BaseTestResourceTrackerV2API):

    def setUp(self):
        super(TestResourceAPIView, self).setUp()
        self._list_create_url = reverse('api_resource_list_create',  kwargs={"resource_group_id": self.cluster.id})
        self._details_url = reverse('api_resource_details', kwargs={"resource_group_id": self.cluster.id,
                                                                    "pk": self.server1.id})

    def test_resource_group_resources_list(self):
        response = self.client.get(self._list_create_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], self.cluster.resources.count())
        for resource in response.json()['results']:
            self.assertTrue("id" in resource)
            self.assertTrue("name" in resource)
            self.assertTrue("service_catalog_instance" in resource)
            self.assertTrue("resource_attributes" in resource)

    def test_resource_list_filter_by_name(self):
        # test existing name
        url = self._list_create_url + f"?name={self.server1.name}"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, response.json()["count"])
        serializer = ResourceSerializer(self.server1)
        self.assertEqual(response.data['results'],  [serializer.data])

        # test non existing name
        url = self._list_create_url + f"?name=do_not_exist"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, response.data['count'])

    def test_create_resource_with_valid_attributes(self):
        data = {
            "name": "new_resource",
            "service_catalog_instance": None,
            "resource_attributes": [
                {
                    "name": "core",
                    "value": "12"
                }
            ]
        }
        response = self.client.post(self._list_create_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_resource_with_non_valid_attributes(self):
        data = {
            "name": "new_resource",
            "service_catalog_instance": None,
            "resource_attributes": [
                {
                    "name": "CPU",
                    "value": "12"
                }
            ]
        }
        response = self.client.post(self._list_create_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Attribute does not exist", str(response.data["resource_attributes"]))

    def test_create_resource_with_non_linked_attributes(self):
        data = {
            "name": "new_resource",
            "service_catalog_instance": None,
            "resource_attributes": [
                {
                    "name": "vcpu",
                    "value": "12"
                }
            ]
        }
        response = self.client.post(self._list_create_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("not linked to resource group", str(response.data["resource_attributes"]))

    def test_create_resource_with_twice_same_attribute(self):
        data = {
            "name": "new_resource",
            "service_catalog_instance": None,
            "resource_attributes": [
                {
                    "name": "core",
                    "value": "12"
                },
                {
                    "name": "core",
                    "value": "15"
                }
            ]
        }
        response = self.client.post(self._list_create_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Duplicate attribute", str(response.data["resource_attributes"]))

    def test_update_resource(self):
        data = {
            "name": "server-1-new-name",
            "service_catalog_instance": None,
            "resource_attributes": [
                {
                    "name": "core",
                    "value": 1
                },
                {
                    "name": "memory",
                    "value": 2
                }
            ]
        }
        response = self.client.put(self._details_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertTrue("id" in response_json)
        self.assertTrue("name" in response_json)
        self.assertEqual("server-1-new-name", response_json["name"])

        self.server1.refresh_from_db()
        self.assertEqual("server-1-new-name", self.server1.name)
        self.assertEqual(1, self.server1.resource_attributes.get(attribute_definition=self.core_attribute).value)
        self.assertEqual(2, self.server1.resource_attributes.get(attribute_definition=self.memory_attribute).value)

    def test_update_resource_edit_attribute_that_was_not_declared_yet(self):
        Transformer.objects.create(resource_group=self.cluster,
                                   attribute_definition=self.vcpu_attribute)

        data = {
            "name": "server-1-new-name",
            "service_catalog_instance": None,
            "resource_attributes": [
                {
                    "name": "core",
                    "value": 1
                },
                {
                    "name": "memory",
                    "value": 2
                },
                {
                    "name": "vcpu",
                    "value": 2
                }
            ]
        }
        response = self.client.put(self._details_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.server1.refresh_from_db()
        self.assertEqual(2, self.server1.resource_attributes.get(attribute_definition=self.vcpu_attribute).value)

    def test_update_resource_with_non_valid_attributes(self):
        data = {
            "name": "new_resource",
            "service_catalog_instance": None,
            "resource_attributes": [
                {
                    "name": "CPU",
                    "value": "12"
                }
            ]
        }
        response = self.client.put(self._details_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Attribute does not exist", str(response.data["resource_attributes"]))

    def test_update_resource_patch_one_attribute(self):
        Transformer.objects.create(resource_group=self.cluster,
                                   attribute_definition=self.vcpu_attribute)

        data = {
            "name": "server-1-new-name",
            "service_catalog_instance": None,
            "resource_attributes": [
                {
                    "name": "memory",
                    "value": 2
                }
            ]
        }
        response = self.client.patch(self._details_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.server1.refresh_from_db()
        self.assertEqual(10, self.server1.resource_attributes.get(attribute_definition=self.core_attribute).value)
        self.assertEqual(2, self.server1.resource_attributes.get(attribute_definition=self.memory_attribute).value)

    def test_delete_resource(self):
        resource_to_delete = self.server1.id
        response = self.client.delete(self._details_url,format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Resource.objects.filter(id=resource_to_delete).exists())
