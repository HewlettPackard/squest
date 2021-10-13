from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestAttributeDefinitionUpdate(BaseTestAPI):

    def setUp(self):
        super(TestAttributeDefinitionUpdate, self).setUp()
        self.url = reverse('api_attribute_definition_retrieve_update_delete',
                           args=[self.rg_physical_servers.id,
                                 self.rg_physical_servers_cpu_attribute.id])

    def _check_attribute_definition_update(self, data):
        attribute_id = self.rg_physical_servers_cpu_attribute.id
        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.rg_physical_servers_cpu_attribute.refresh_from_db()
        self.assertEqual(self.rg_physical_servers_cpu_attribute.id,  attribute_id)
        self.assertEqual(self.rg_physical_servers_cpu_attribute.name, data["name"])
        if data["consume_from"] is not None:
            self.assertEqual(self.rg_physical_servers_cpu_attribute.consume_from.id, data["consume_from"])
        else:
            self.assertIsNone(self.rg_physical_servers_cpu_attribute.consume_from)
        if data["produce_for"] is not None:
            self.assertEqual(self.rg_physical_servers_cpu_attribute.produce_for.id, data["produce_for"])
        else:
            self.assertIsNone(self.rg_physical_servers_cpu_attribute.produce_for)
        self.assertEqual(self.rg_physical_servers_cpu_attribute.help_text, data["help_text"])

    def test_attribute_definition_update(self):
        data = {
            "id": self.rg_physical_servers_cpu_attribute.id,
            "name": "updated_name",
            "consume_from": None,
            "produce_for": None,
            "help_text": "updated_help"
        }
        self._check_attribute_definition_update(data)

    def test_attribute_definition_update_no_id(self):
        data = {
            "name": "updated_name",
            "consume_from": None,
            "produce_for": None,
            "help_text": "updated_help"
        }
        self._check_attribute_definition_update(data)

    def test_attribute_definition_update_wrong_id(self):
        data = {
            "id": self.rg_physical_servers_memory_attribute.id,
            "name": "updated_name",
            "consume_from": None,
            "produce_for": None,
            "help_text": "updated_help"
        }
        self._check_attribute_definition_update(data)

    def test_cannot_update_attribute_definition_when_wrong_rg(self):
        data = {
            "id": self.rg_physical_servers_cpu_attribute.id,
            "name": "updated_name",
            "consume_from": None,
            "produce_for": None,
            "help_text": "updated_help"
        }
        url = reverse('api_attribute_definition_retrieve_update_delete',
                      args=[self.rg_ocp_workers.id,
                            self.rg_physical_servers_cpu_attribute.id])
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
