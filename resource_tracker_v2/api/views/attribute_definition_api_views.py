from Squest.utils.squest_api_views import SquestListCreateAPIView, SquestRetrieveUpdateDestroyAPIView
from resource_tracker_v2.api.serializers.attribute_definition_serializers import AttributeDefinitionSerializer
from resource_tracker_v2.filters.attribute_definition_filter import AttributeDefinitionFilter
from resource_tracker_v2.models import AttributeDefinition


class AttributeDefinitionList(SquestListCreateAPIView):
    queryset = AttributeDefinition.objects.all()
    serializer_class = AttributeDefinitionSerializer
    filterset_class = AttributeDefinitionFilter


class AttributeDefinitionDetails(SquestRetrieveUpdateDestroyAPIView):
    queryset = AttributeDefinition.objects.all()
    serializer_class = AttributeDefinitionSerializer
