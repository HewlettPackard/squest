from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker.models import ResourcePoolAttributeDefinition
from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestResourcePoolAttributeDefinitionDelete(BaseTestAPI):

    def setUp(self):
        super(TestResourcePoolAttributeDefinitionDelete, self).setUp()
        self.to_be_deleted_id = self.rp_vcenter_vcpu_attribute.id
        self.url = reverse('api_resource_pool_attribute_definition_retrieve_update_delete',
                           args=[self.rp_vcenter.id,
                                 self.rp_vcenter_vcpu_attribute.id])

    def test_attribute_definition_delete(self):
        self.assertTrue(ResourcePoolAttributeDefinition.objects.filter(id=self.to_be_deleted_id).exists())
        response = self.client.delete(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ResourcePoolAttributeDefinition.objects.filter(id=self.to_be_deleted_id).exists())

    def test_cannot_delete_attribute_definition_when_wrong_rg(self):
        url = reverse('api_resource_pool_attribute_definition_retrieve_update_delete',
                      args=[self.rp_ocp_workers.id,
                            self.rp_vcenter_vcpu_attribute.id])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
