from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker_v2.api.serializers.attribute_definition_serializers import AttributeDefinitionSerializer
from resource_tracker_v2.models import AttributeDefinition
from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2API


class TestAttributeDefinitionAPIViews(BaseTestResourceTrackerV2API):

    def setUp(self):
        super(TestAttributeDefinitionAPIViews, self).setUp()
        self._list_create_url = reverse('api_attributedefinition_list_create')
        self._details_url = reverse('api_attributedefinition_details', kwargs={'pk': self.core_attribute.id})

    def test_create_valid_attribute(self):
        data = {
            "name": "new-attribute",
            "description": "this-is-new"
        }
        number_attribute_before = AttributeDefinition.objects.all().count()
        response = self.client.post(self._list_create_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AttributeDefinition.objects.latest('id').name, data["name"])
        self.assertEqual(AttributeDefinition.objects.latest('id').description, data["description"])
        self.assertEqual(number_attribute_before + 1, AttributeDefinition.objects.all().count())

    def test_create_attribute_name_exist_already(self):
        data = {
            "name": self.core_attribute.name,
        }
        response = self.client.post(self._list_create_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Attribute Definition With This Name Already Exists", response.data["name"][0].title())

    def test_attribute_definition_list(self):
        response = self.client.get(self._list_create_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], AttributeDefinition.objects.all().count())
        for attribute_definition in response.json()['results']:
            self.assertTrue("id" in attribute_definition)
            self.assertTrue("name" in attribute_definition)
            self.assertTrue("description" in attribute_definition)

    def test_resource_group_list_filter_by_name(self):
        url = self._list_create_url + f"?name={self.core_attribute.name}"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, response.data['count'])
        serializer = AttributeDefinitionSerializer(self.core_attribute)
        self.assertEqual(response.data['results'], [serializer.data])

        # test non existing name
        url = self._list_create_url + f"?name=do_not_exist"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, response.data['count'])

    def test_update_attribute_definition(self):
        data = {
            "name": "updated",
            "description": "this-is-new"
        }
        response = self.client.put(self._details_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.core_attribute.refresh_from_db()
        self.assertEqual(self.core_attribute.name, "updated")
        self.assertEqual(self.core_attribute.description, "this-is-new")

    def test_delete_attribute_definition(self):
        id_to_delete = self.core_attribute.id
        response = self.client.delete(self._details_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(AttributeDefinition.objects.filter(id=id_to_delete))

    def test_get_attribute_definition_details(self):
        response = self.client.get(self._details_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("id" in response.json())
        self.assertTrue("name" in response.json())
        self.assertTrue("description" in response.json())
        self.assertEqual(response.json()["id"], self.core_attribute.id)
        self.assertEqual(response.json()["name"], self.core_attribute.name)
