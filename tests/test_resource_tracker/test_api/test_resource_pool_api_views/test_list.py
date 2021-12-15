from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker.api.serializers.resource_pool.resource_pool_serializer import ResourcePoolSerializer
from resource_tracker.models import ResourcePool
from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestResourcePoolList(BaseTestAPI):

    def setUp(self):
        super(TestResourcePoolList, self).setUp()
        self.url = reverse('api_resource_pool_list_create')

    def test_resource_pool_list(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ResourcePool.objects.all().count(), len(response.data))
        all_instances = ResourcePool.objects.all()
        serializer = ResourcePoolSerializer(all_instances, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_resource_pool_list_filter_by_name(self):
        # test existing name
        testing_rp = ResourcePool.objects.create(name="rp-test")
        url = reverse('api_resource_pool_list_create') + f"?name={testing_rp.name}"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))
        serializer = ResourcePoolSerializer(testing_rp)
        self.assertEqual(response.data,  [serializer.data])

        # test non existing name
        url = reverse('api_resource_pool_list_create') + f"?name=do_not_exist"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(response.data))
