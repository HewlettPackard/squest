from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker.models import ResourcePoolAttributeDefinition
from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestAttributeDefinitionCreate(BaseTestAPI):

    def setUp(self):
        super(TestAttributeDefinitionCreate, self).setUp()
        self.url = reverse('api_resource_pool_attribute_definition_list_create', args=[self.rp_vcenter.id])

    def _check_attribute_definition_create(self, data):
        number_attribute_before = ResourcePoolAttributeDefinition.objects.all().count()
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ResourcePoolAttributeDefinition.objects.latest('id').name, data["name"])
        self.assertEqual(ResourcePoolAttributeDefinition.objects.latest('id').resource_pool.id,
                         self.rp_vcenter.id)
        if "over_commitment_producers" in data:
            self.assertEqual(ResourcePoolAttributeDefinition.objects.latest('id').over_commitment_producers,
                             data["over_commitment_producers"])
        else:
            self.assertEqual(ResourcePoolAttributeDefinition.objects.latest('id').over_commitment_producers,
                             1.0)
        if "over_commitment_consumers" in data:
            self.assertEqual(ResourcePoolAttributeDefinition.objects.latest('id').over_commitment_consumers,
                             data["over_commitment_consumers"])
        else:
            self.assertEqual(ResourcePoolAttributeDefinition.objects.latest('id').over_commitment_producers,
                             1.0)
        self.assertEqual(number_attribute_before + 1,
                         ResourcePoolAttributeDefinition.objects.all().count())

    def test_rp_attribute_definition_create(self):
        data = {
            "name": "new_rp_attribute",
            "over_commitment_producers": 1.25,
            "over_commitment_consumers": 2.15
        }
        self._check_attribute_definition_create(data)

    def test_rp_attribute_definition_no_over_commitment(self):
        data = {
            "name": "new_rp_attribute",
        }
        self._check_attribute_definition_create(data)

    def test_cannot_create_rp_attribute_definition_when_wrong_over_commitment(self):
        data = {
            "name": "new_rp_attribute",
            "over_commitment_producers": "text",
            "over_commitment_consumers": 2.15
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
