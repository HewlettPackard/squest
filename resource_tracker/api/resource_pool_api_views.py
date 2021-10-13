from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from resource_tracker.api.serializers.resource_pool.resource_pool_serializer import ResourcePoolSerializer, \
    ResourcePoolSerializerRead, ResourcePoolAttributeDefinitionSerializer
from resource_tracker.models import ResourcePool, ResourcePoolAttributeDefinition


class ResourcePoolList(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = ResourcePool.objects.all()
    serializer_class = ResourcePoolSerializer


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

    def create(self, request, *args, **kwargs):
        request.data['resource_pool'] = self.kwargs.get('pk', None)
        return super(PoolAttributeDefinitionList, self).create(request, *args, **kwargs)


class PoolAttributeDefinitionDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ResourcePoolAttributeDefinitionSerializer
    lookup_url_kwarg = "attribute_definition_id"

    def get_queryset(self):
        resource_group_id = self.kwargs.get("pk")
        return ResourcePoolAttributeDefinition.objects.filter(resource_pool_id=resource_group_id)

    def update(self, request, *args, **kwargs):
        request.data['resource_pool'] = self.kwargs.get('pk', None)
        return super(PoolAttributeDefinitionDetails, self).update(request, *args, **kwargs)
