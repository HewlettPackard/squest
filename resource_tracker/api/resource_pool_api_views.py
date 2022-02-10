from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from resource_tracker.api.serializers.resource_pool.resource_pool_serializer import ResourcePoolSerializer, \
    ResourcePoolSerializerRead, ResourcePoolAttributeDefinitionSerializer
from resource_tracker.models import ResourcePool, ResourcePoolAttributeDefinition


class ResourcePoolList(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ResourcePoolSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned resource pool to a given name,
        by filtering against a `name` query parameter in the URL.
        """
        queryset = ResourcePool.objects.all()
        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name=name)
        return queryset


class ResourcePoolDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = ResourcePool.objects.all()
    serializer_class = ResourcePoolSerializerRead


class PoolAttributeDefinitionList(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ResourcePoolAttributeDefinitionSerializer

    def get_queryset(self):
        resource_group_id = self.kwargs.get("pk")
        return ResourcePoolAttributeDefinition.objects.filter(resource_pool_id=resource_group_id)

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            kwargs['data']['resource_pool'] = self.kwargs.get('pk', None)
        return super(PoolAttributeDefinitionList, self).get_serializer(*args, **kwargs)


class PoolAttributeDefinitionDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ResourcePoolAttributeDefinitionSerializer
    lookup_url_kwarg = "attribute_definition_id"

    def get_queryset(self):
        resource_group_id = self.kwargs.get("pk")
        return ResourcePoolAttributeDefinition.objects.filter(resource_pool_id=resource_group_id)

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            kwargs['data']['resource_pool'] = self.kwargs.get('pk', None)
        return super(PoolAttributeDefinitionDetails, self).get_serializer(*args, **kwargs)
