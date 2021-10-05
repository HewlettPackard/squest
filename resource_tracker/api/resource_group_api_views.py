from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from resource_tracker.api.serializers.resource_group_serializer import ResourceGroupSerializer
from resource_tracker.models import ResourceGroup


class ResourceGroupList(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = ResourceGroup.objects.all()
    serializer_class = ResourceGroupSerializer


class ResourceGroupDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = ResourceGroup.objects.all()
    serializer_class = ResourceGroupSerializer
