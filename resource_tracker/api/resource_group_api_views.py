from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from resource_tracker.api.serializers.resource_group_serializer import ResourceGroupSerializer, \
    ResourceGroupSerializerRead, ResourceGroupAttributeDefinitionSerializer
from resource_tracker.models import ResourceGroup, ResourceGroupAttributeDefinition


class ResourceGroupList(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = ResourceGroup.objects.all()
    serializer_class = ResourceGroupSerializer


class ResourceGroupDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = ResourceGroup.objects.all()
    serializer_class = ResourceGroupSerializerRead


class AttributeDefinitionList(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ResourceGroupAttributeDefinitionSerializer

    def get_queryset(self):
        resource_group_id = self.kwargs.get("pk")
        return ResourceGroupAttributeDefinition.objects.filter(resource_group_definition_id=resource_group_id)


class AttributeDefinitionDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ResourceGroupAttributeDefinitionSerializer
    lookup_url_kwarg = "attribute_definition_id"

    def get_queryset(self):
        resource_group_id = self.kwargs.get("pk")
        return ResourceGroupAttributeDefinition.objects.filter(resource_group_definition_id=resource_group_id)
