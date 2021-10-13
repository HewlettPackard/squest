from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker.models import ResourceGroupTextAttributeDefinition
from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestTextAttributeDefinitionCreate(BaseTestAPI):

    def setUp(self):
        super(TestTextAttributeDefinitionCreate, self).setUp()
        self.url = reverse('api_text_attribute_definition_list_create', args=[self.rg_physical_servers.id])

    def _check_text_attribute_definition_create(self, data):
        number_text_attribute_before = ResourceGroupTextAttributeDefinition.objects.all().count()
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ResourceGroupTextAttributeDefinition.objects.latest('id').name, data["name"])
        self.assertEqual(ResourceGroupTextAttributeDefinition.objects.latest('id').help_text, data["help_text"])
        self.assertEqual(ResourceGroupTextAttributeDefinition.objects.latest('id').resource_group_definition.id,
                         self.rg_physical_servers.id)
        self.assertEqual(number_text_attribute_before + 1,
                         ResourceGroupTextAttributeDefinition.objects.all().count())

    def test_text_attribute_definition_create(self):
        data = {
            "name": "new_attribute",
            "help_text": "help"
        }
        self._check_text_attribute_definition_create(data)

    def test_text_attribute_definition_create_with_specified_rg(self):
        data = {
            "name": "new_attribute",
            "help_text": "help",
            "resource_group_definition": 14
        }
        self._check_text_attribute_definition_create(data)
