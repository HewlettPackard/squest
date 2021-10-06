from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker.models import Resource
from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestResourceGetDetails(BaseTestAPI):

    def setUp(self):
        super(TestResourceGetDetails, self).setUp()
        # get a resource to get
        self.resource_to_delete = Resource.objects.get(name="server-1")
        self.url = reverse('api_resource_retrieve_delete',  args=[self.rg_physical_servers.id,
                                                                  self.resource_to_delete.id])

    def test_get_resource(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("id" in response.json())
        self.assertTrue("name" in response.json())
        self.assertTrue("attributes" in response.json())
        self.assertTrue("text_attributes" in response.json())
