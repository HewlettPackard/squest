from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker.api.serializers.resource_group.attribute_definition_serializers import \
    ResourceGroupAttributeDefinitionSerializer
from resource_tracker.models import ResourceGroupAttributeDefinition
from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestAttributeDefinitionList(BaseTestAPI):

    def setUp(self):
        super(TestAttributeDefinitionList, self).setUp()
        self.url = reverse('api_attribute_definition_list_create', args=[self.rg_physical_servers.id])

    def test_attribute_definition_list(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ResourceGroupAttributeDefinition.objects.
                         filter(resource_group_definition=self.rg_physical_servers).count(),
                         len(response.data))
        all_instances = ResourceGroupAttributeDefinition.objects.\
            filter(resource_group_definition=self.rg_physical_servers)
        serializer = ResourceGroupAttributeDefinitionSerializer(all_instances, many=True)
        self.assertEqual(response.data, serializer.data)
