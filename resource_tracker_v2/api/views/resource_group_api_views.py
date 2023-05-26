from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from resource_tracker_v2.api.serializers.resource_group_serializers import ResourceGroupSerializer
from resource_tracker_v2.filters.resource_group_filter import ResourceGroupFilter
from resource_tracker_v2.models import ResourceGroup


class ResourceGroupList(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = ResourceGroup.objects.all()
    serializer_class = ResourceGroupSerializer
    filterset_class = ResourceGroupFilter


class ResourceGroupDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = ResourceGroup.objects.all()
    serializer_class = ResourceGroupSerializer
