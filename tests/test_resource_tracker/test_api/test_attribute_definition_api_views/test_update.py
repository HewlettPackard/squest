from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestAttributeDefinitionUpdate(BaseTestAPI):

    def setUp(self):
        super(TestAttributeDefinitionUpdate, self).setUp()
        self.url = reverse('api_attribute_definition_retrieve_update_delete',
                           args=[self.rg_physical_servers.id,
                                 self.rg_physical_servers_cpu_attribute.id])

        self.data = {
            "id": self.rg_physical_servers_cpu_attribute.id,
            "name": "updated_name",
            "consume_from": None,
            "produce_for": None,
            "help_text": "updated_help"
        }

    def test_attribute_definition_update(self):
        response = self.client.put(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.rg_physical_servers_cpu_attribute.refresh_from_db()
        self.assertEqual(self.rg_physical_servers_cpu_attribute.name, self.data["name"])
        if self.data["consume_from"] is not None:
            self.assertEqual(self.rg_physical_servers_cpu_attribute.consume_from.id, self.data["consume_from"])
        else:
            self.assertIsNone(self.rg_physical_servers_cpu_attribute.consume_from)
        if self.data["produce_for"] is not None:
            self.assertEqual(self.rg_physical_servers_cpu_attribute.produce_for.id, self.data["produce_for"])
        else:
            self.assertIsNone(self.rg_physical_servers_cpu_attribute.produce_for)
        self.assertEqual(self.rg_physical_servers_cpu_attribute.help_text, self.data["help_text"])

    def test_cannot_update_attribute_definition_when_wrong_rg(self):
        url = reverse('api_attribute_definition_retrieve_update_delete',
                      args=[self.rg_ocp_workers.id,
                            self.rg_physical_servers_cpu_attribute.id])
        response = self.client.put(url, data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
