from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker.api.serializers.resource_group.resource_serializers import ResourceSerializer
from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestResourceList(BaseTestAPI):

    def setUp(self):
        super(TestResourceList, self).setUp()
        self.url = reverse('api_resource_list_create',  args=[self.rg_physical_servers.id])

    def test_resource_group_resources_list(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 4)
        for resource in response.json():
            self.assertTrue("id" in resource)
            self.assertTrue("name" in resource)
            self.assertTrue("service_catalog_instance" in resource)
            self.assertTrue("attributes" in resource)
            self.assertTrue("text_attributes" in resource)

    def test_resource_list_filter_by_name(self):
        # test existing name
        testing_resource = self.rg_physical_servers.create_resource(name=f"testing")
        url = reverse('api_resource_list_create',  args=[self.rg_physical_servers.id]) + f"?name={testing_resource.name}"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))
        serializer = ResourceSerializer(testing_resource)
        self.assertEqual(response.data,  [serializer.data])

        # test non existing name
        url = reverse('api_resource_list_create',  args=[self.rg_physical_servers.id]) + f"?name=do_not_exist"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(response.data))
