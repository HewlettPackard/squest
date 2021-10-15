from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker.models import ResourceGroupAttributeDefinition
from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestAttributeDefinitionCreate(BaseTestAPI):

    def setUp(self):
        super(TestAttributeDefinitionCreate, self).setUp()
        self.url = reverse('api_attribute_definition_list_create', args=[self.rg_physical_servers.id])

    def _check_attribute_definition_create(self, data):
        number_attribute_before = ResourceGroupAttributeDefinition.objects.all().count()
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ResourceGroupAttributeDefinition.objects.latest('id').name, data["name"])
        self.assertEqual(ResourceGroupAttributeDefinition.objects.latest('id').resource_group.id,
                         self.rg_physical_servers.id)
        try:
            self.assertEqual(ResourceGroupAttributeDefinition.objects.latest('id').consume_from.id, data["consume_from"])
            self.assertEqual(ResourceGroupAttributeDefinition.objects.latest('id').produce_for.id, data["produce_for"])
        except AttributeError:  # consumer and producer may be None
            pass
        self.assertEqual(ResourceGroupAttributeDefinition.objects.latest('id').help_text, data["help_text"])
        self.assertEqual(number_attribute_before + 1,
                         ResourceGroupAttributeDefinition.objects.all().count())

    def test_attribute_definition_create(self):
        data = {
            "name": "new_attribute",
            "consume_from": None,
            "produce_for": None,
            "help_text": "help"
        }
        self._check_attribute_definition_create(data)

    def test_attribute_definition_create_with_attached_pool(self):
        data = {
            "name": "new_attribute",
            "consume_from": self.rp_vcenter_memory_attribute.id,
            "produce_for": self.rp_vcenter_vcpu_attribute.id,
            "help_text": ""
        }
        self._check_attribute_definition_create(data)

    def test_cannot_create_attribute_definition_when_non_existing_consumer(self):
        data = {
            "name": "new_attribute",
            "consume_from": 99999,
            "produce_for": None,
            "help_text": ""
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
