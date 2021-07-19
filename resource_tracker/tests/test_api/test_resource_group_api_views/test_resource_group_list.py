from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker.api.serializers.resource_group_serializer import ResourceGroupSerializer
from resource_tracker.models import ResourceGroup
from resource_tracker.tests.test_api.base_test_api import BaseTestAPI


class TestResourceGroupList(BaseTestAPI):

    def setUp(self):
        super(TestResourceGroupList, self).setUp()
        self.url = reverse('api_resource_group_list')

    def test_resource_group_list(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ResourceGroup.objects.all().count(), len(response.data))
        all_instances = ResourceGroup.objects.all()
        serializer = ResourceGroupSerializer(all_instances, many=True)
        self.assertEqual(response.data, serializer.data)
