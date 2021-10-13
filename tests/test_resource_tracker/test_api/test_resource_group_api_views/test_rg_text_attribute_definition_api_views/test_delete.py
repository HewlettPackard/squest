from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker.models import ResourceGroupTextAttributeDefinition
from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestTextAttributeDefinitionDelete(BaseTestAPI):

    def setUp(self):
        super(TestTextAttributeDefinitionDelete, self).setUp()
        self.to_be_deleted_id = self.rg_physical_servers_description.id
        self.url = reverse('api_text_attribute_definition_retrieve_update_delete',
                           args=[self.rg_physical_servers.id,
                                 self.rg_physical_servers_description.id])

    def test_text_attribute_definition_delete(self):
        self.assertTrue(ResourceGroupTextAttributeDefinition.objects.filter(id=self.to_be_deleted_id).exists())
        response = self.client.delete(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ResourceGroupTextAttributeDefinition.objects.filter(id=self.to_be_deleted_id).exists())

    def test_cannot_delete_text_attribute_definition_when_wrong_rg(self):
        url = reverse('api_text_attribute_definition_retrieve_update_delete',
                      args=[self.rg_ocp_projects.id,
                            self.rg_physical_servers_description.id])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
