from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestAttributeDefinitionDetail(BaseTestAPI):

    def setUp(self):
        super(TestAttributeDefinitionDetail, self).setUp()
        self.url = reverse('api_attribute_definition_retrieve_update_delete',
                           args=[self.rg_physical_servers.id,
                                 self.rg_physical_servers_cpu_attribute.id])

    def test_attribute_definition_details(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("id" in response.json())
        self.assertTrue("name" in response.json())
        self.assertTrue("consume_from" in response.json())
        self.assertTrue("produce_for" in response.json())
        self.assertTrue("help_text" in response.json())
        self.assertEqual(response.json()["id"], self.rg_physical_servers_cpu_attribute.id)
        self.assertEqual(response.json()["name"], self.rg_physical_servers_cpu_attribute.name)
        if response.json()["consume_from"]:
            self.assertEqual(response.json()["consume_from"], self.rg_physical_servers_cpu_attribute.consume_from.id)
        if response.json()["produce_for"]:
            self.assertEqual(response.json()["produce_for"], self.rg_physical_servers_cpu_attribute.produce_for.id)
        self.assertEqual(response.json()["help_text"], self.rg_physical_servers_cpu_attribute.help_text)

    def test_cannot_get_attribute_definition_detail_when_wrong_rg(self):
        url = reverse('api_attribute_definition_retrieve_update_delete',
                      args=[self.rg_ocp_workers.id,
                            self.rg_physical_servers_cpu_attribute.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
