from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from resource_tracker_v2.api.serializers.attribute_definition_serializers import AttributeDefinitionSerializer
from resource_tracker_v2.filters.attribute_definition_filter import AttributeDefinitionFilter
from resource_tracker_v2.models import AttributeDefinition


class AttributeDefinitionList(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = AttributeDefinition.objects.all()
    serializer_class = AttributeDefinitionSerializer
    filterset_class = AttributeDefinitionFilter


class AttributeDefinitionDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = AttributeDefinition.objects.all()
    serializer_class = AttributeDefinitionSerializer
