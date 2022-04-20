from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker.api.serializers.resource_group.text_attribute_definition_serializers import \
    ResourceGroupTextAttributeDefinitionSerializer
from resource_tracker.models import ResourceGroupTextAttributeDefinition
from tests.test_resource_tracker.test_api.base_test_api import BaseTestAPI


class TestTextAttributeDefinitionList(BaseTestAPI):

    def setUp(self):
        super(TestTextAttributeDefinitionList, self).setUp()
        self.url = reverse('api_text_attribute_definition_list_create', args=[self.rg_physical_servers.id])

    def test_text_attribute_definition_list(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ResourceGroupTextAttributeDefinition.objects.
                         filter(resource_group=self.rg_physical_servers).count(),
                         response.data['count'])
        all_instances = ResourceGroupTextAttributeDefinition.objects.\
            filter(resource_group=self.rg_physical_servers)
        serializer = ResourceGroupTextAttributeDefinitionSerializer(all_instances, many=True)
        self.assertEqual(response.data['results'], serializer.data)
