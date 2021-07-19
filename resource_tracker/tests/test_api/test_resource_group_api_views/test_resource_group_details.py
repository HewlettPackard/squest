from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker.tests.test_api.base_test_api import BaseTestAPI


class TestResourceGroupDetail(BaseTestAPI):

    def setUp(self):
        super(TestResourceGroupDetail, self).setUp()
        self.url = reverse('api_resource_group_details',  args=[self.rg_physical_servers.id])

    def test_resource_group_details(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("id" in response.json())
        self.assertTrue("name" in response.json())
        self.assertTrue("resources" in response.json())
