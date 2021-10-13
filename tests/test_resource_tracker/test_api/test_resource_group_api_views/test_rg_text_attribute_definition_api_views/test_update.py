from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestTextAttributeDefinitionUpdate(BaseTestAPI):

    def setUp(self):
        super(TestTextAttributeDefinitionUpdate, self).setUp()
        self.url = reverse('api_text_attribute_definition_retrieve_update_delete',
                           args=[self.rg_physical_servers.id,
                                 self.rg_physical_servers_description.id])

        self.data = {
            "id": self.rg_physical_servers_description.id,
            "name": "updated_name",
            "help_text": "updated_help"
        }

    def _check_text_attribute_definition_update(self, data):
        attribute_id = self.rg_physical_servers_description.id
        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.rg_physical_servers_description.refresh_from_db()
        self.assertEqual(self.rg_physical_servers_description.id, attribute_id)
        self.assertEqual(self.rg_physical_servers_description.name, data["name"])
        self.assertEqual(self.rg_physical_servers_description.help_text, data["help_text"])

    def test_text_attribute_definition_update(self):
        self._check_text_attribute_definition_update(self.data)

    def test_text_attribute_definition_update_no_id(self):
        data = {
            "name": "updated_name",
            "help_text": "updated_help"
        }
        self._check_text_attribute_definition_update(data)

    def test_text_attribute_definition_update_wrong_id(self):
        data = {
            "id": self.rg_ocp_projects_cpu_attribute.id,
            "name": "updated_name",
            "help_text": "updated_help"
        }
        self._check_text_attribute_definition_update(data)

    def test_cannot_update_attribute_definition_when_wrong_rg(self):
        url = reverse('api_text_attribute_definition_retrieve_update_delete',
                      args=[self.rg_ocp_workers.id,
                            self.rg_physical_servers_description.id])
        response = self.client.put(url, data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
