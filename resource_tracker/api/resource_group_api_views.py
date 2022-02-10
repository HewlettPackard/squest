from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from resource_tracker.api.serializers.resource_group.attribute_definition_serializers import \
    ResourceGroupAttributeDefinitionSerializer
from resource_tracker.api.serializers.resource_group.resource_group_serializers import ResourceGroupSerializer, \
    ResourceGroupSerializerRead
from resource_tracker.api.serializers.resource_group.text_attribute_definition_serializers import \
    ResourceGroupTextAttributeDefinitionSerializer
from resource_tracker.models import ResourceGroup, ResourceGroupAttributeDefinition, \
    ResourceGroupTextAttributeDefinition


class ResourceGroupList(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ResourceGroupSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned resource group to a given name,
        by filtering against a `name` query parameter in the URL.
        """
        queryset = ResourceGroup.objects.all()
        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name=name)
        return queryset


class ResourceGroupDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = ResourceGroup.objects.all()
    serializer_class = ResourceGroupSerializerRead


class AttributeDefinitionList(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ResourceGroupAttributeDefinitionSerializer

    def get_queryset(self):
        resource_group_id = self.kwargs.get("pk")
        return ResourceGroupAttributeDefinition.objects.filter(resource_group_id=resource_group_id)

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            kwargs['data']['resource_group'] = self.kwargs.get('pk', None)
        return super(AttributeDefinitionList, self).get_serializer(*args, **kwargs)


class AttributeDefinitionDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ResourceGroupAttributeDefinitionSerializer
    lookup_url_kwarg = "attribute_definition_id"

    def get_queryset(self):
        resource_group_id = self.kwargs.get("pk")
        return ResourceGroupAttributeDefinition.objects.filter(resource_group_id=resource_group_id)

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            kwargs['data']['resource_group'] = self.kwargs.get('pk', None)
        return super(AttributeDefinitionDetails, self).get_serializer(*args, **kwargs)


class TextAttributeDefinitionList(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ResourceGroupTextAttributeDefinitionSerializer

    def get_queryset(self):
        resource_group_id = self.kwargs.get("pk")
        return ResourceGroupTextAttributeDefinition.objects.filter(resource_group_id=resource_group_id)

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            kwargs['data']['resource_group'] = self.kwargs.get('pk', None)
        return super(TextAttributeDefinitionList, self).get_serializer(*args, **kwargs)


class TextAttributeDefinitionDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ResourceGroupTextAttributeDefinitionSerializer
    lookup_url_kwarg = "text_attribute_definition_id"

    def get_queryset(self):
        resource_group_id = self.kwargs.get("pk")
        return ResourceGroupTextAttributeDefinition.objects.filter(resource_group_id=resource_group_id)

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            kwargs['data']['resource_group'] = self.kwargs.get('pk', None)
        return super(TextAttributeDefinitionDetails, self).get_serializer(*args, **kwargs)
