from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestResourceGroupUpdate(BaseTestAPI):

    def setUp(self):
        super(TestResourceGroupUpdate, self).setUp()
        self.url = reverse('api_resource_group_details',  args=[self.rg_physical_servers.id])

    def test_update(self):
        """
        Update is partial. attribute_definitions and text_attribute_definitions are not handled
        """
        data = {
            "name": "updated",
            "tags": ["new_tag"]
        }
        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.rg_physical_servers.refresh_from_db()
        self.assertEqual(self.rg_physical_servers.name, "updated")
        self.assertEqual(self.rg_physical_servers.tags.all().first().name, "new_tag")
