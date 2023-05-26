from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker_v2.api.serializers.resource_serializer import ResourceSerializer
from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2API


class TestResourceAPIView(BaseTestResourceTrackerV2API):

    def setUp(self):
        super(TestResourceAPIView, self).setUp()
        self._list_create_url = reverse('api_resource_list_create',  kwargs={"resource_group_id": self.cluster.id})

    def test_resource_group_resources_list(self):
        response = self.client.get(self._list_create_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], self.cluster.resources.count())
        for resource in response.json()['results']:
            self.assertTrue("id" in resource)
            self.assertTrue("name" in resource)
            self.assertTrue("service_catalog_instance" in resource)
            self.assertTrue("resource_attributes" in resource)

    def test_resource_list_filter_by_name(self):
        # test existing name
        url = self._list_create_url + f"?name={self.server1.name}"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, response.json()["count"])
        serializer = ResourceSerializer(self.server1)
        self.assertEqual(response.data['results'],  [serializer.data])

        # test non existing name
        url = self._list_create_url + f"?name=do_not_exist"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, response.data['count'])
