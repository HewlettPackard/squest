from django.urls import reverse

from resource_tracker_v2.models import AttributeDefinition
from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2


class TestAttributeDefinitionViews(BaseTestResourceTrackerV2):

    def setUp(self):
        super(TestAttributeDefinitionViews, self).setUp()

    def test_attribute_list(self):
        response = self.client.get(reverse('resource_tracker:attribute_definition_list'))
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data), AttributeDefinition.objects.all().count())

    def test_attribute_create(self):
        url = reverse('resource_tracker:attribute_definition_create')
        data = {
            "name": "new_attribute"
        }
        number_attribute_before = AttributeDefinition.objects.all().count()
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(number_attribute_before + 1, AttributeDefinition.objects.all().count())
        self.assertTrue(AttributeDefinition.objects.filter(name="new_attribute").exists())

    def test_attribute_edit(self):
        args = {
            "attribute_definition_id": self.core_attribute.id,
        }
        url = reverse('resource_tracker:attribute_definition_edit', kwargs=args)

        new_name = "updated"
        data = {
            "name": new_name,
        }
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.core_attribute.refresh_from_db()
        self.assertEqual(self.core_attribute.name, new_name)

    def test_attribute_delete(self):
        args = {
            "attribute_definition_id": self.core_attribute.id,
        }
        url = reverse('resource_tracker:attribute_definition_delete', kwargs=args)

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        self.assertTrue(AttributeDefinition.objects.filter(id=self.core_attribute.id).exists())
        response = self.client.post(url)
        self.assertEqual(302, response.status_code)
        self.assertFalse(AttributeDefinition.objects.filter(id=self.core_attribute.id).exists())
