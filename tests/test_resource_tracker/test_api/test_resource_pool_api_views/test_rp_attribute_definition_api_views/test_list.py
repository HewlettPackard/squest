from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker.api.serializers.resource_pool.resource_pool_serializer import ResourcePoolAttributeDefinitionSerializer
from resource_tracker.models import ResourcePoolAttributeDefinition
from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestResourcePoolAttributeDefinitionList(BaseTestAPI):

    def setUp(self):
        super(TestResourcePoolAttributeDefinitionList, self).setUp()
        self.url = reverse('api_resource_pool_attribute_definition_list_create', args=[self.rp_vcenter.id])

    def test_attribute_definition_list(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ResourcePoolAttributeDefinition.objects.
                         filter(resource_pool=self.rp_vcenter).count(),
                         response.data['count'])
        all_instances = ResourcePoolAttributeDefinition.objects.\
            filter(resource_pool=self.rp_vcenter)
        serializer = ResourcePoolAttributeDefinitionSerializer(all_instances, many=True)
        self.assertEqual(response.data['results'], serializer.data)
