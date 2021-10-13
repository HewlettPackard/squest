from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestTextAttributeDefinitionDetail(BaseTestAPI):

    def setUp(self):
        super(TestTextAttributeDefinitionDetail, self).setUp()
        self.url = reverse('api_text_attribute_definition_retrieve_update_delete',
                           args=[self.rg_physical_servers.id,
                                 self.rg_physical_servers_description.id])

    def test_text_attribute_definition_details(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("id" in response.json())
        self.assertTrue("name" in response.json())
        self.assertTrue("help_text" in response.json())
        self.assertTrue("resource_group_definition" in response.json())
        self.assertEqual(response.json()["id"], self.rg_physical_servers_description.id)
        self.assertEqual(response.json()["name"], self.rg_physical_servers_description.name)
        self.assertEqual(response.json()["help_text"], self.rg_physical_servers_description.help_text)
        self.assertEqual(response.json()["resource_group_definition"], self.rg_physical_servers.id)

    def test_cannot_get_text_attribute_definition_detail_when_wrong_rg(self):
        url = reverse('api_text_attribute_definition_retrieve_update_delete',
                      args=[self.rg_ocp_workers.id,
                            self.rg_physical_servers_description.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
