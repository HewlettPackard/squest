from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker.tests.test_api.base_test_api import BaseTestAPI


class TestResourceGroupResourceList(BaseTestAPI):

    def setUp(self):
        super(TestResourceGroupResourceList, self).setUp()
        self.url = reverse('api_resource_group_resource_list_create',  args=[self.rg_physical_servers.id])

    def test_resource_group_resources_list(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resp_json = response.json()
        self.assertEqual(len(response.json()), 4)
        for resource in response.json():
            self.assertTrue("id" in resource)
            self.assertTrue("name" in resource)
            self.assertTrue("service_catalog_instance" in resource)
            self.assertTrue("attributes" in resource)
