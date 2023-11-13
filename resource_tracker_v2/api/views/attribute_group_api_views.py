from Squest.utils.squest_api_views import SquestListCreateAPIView, SquestRetrieveUpdateDestroyAPIView
from resource_tracker_v2.api.serializers.attribute_group_serializers import AttributeGroupSerializer
from resource_tracker_v2.filters.attribute_group_filter import AttributeGroupFilter
from resource_tracker_v2.models import AttributeGroup


class AttributeGroupList(SquestListCreateAPIView):
    queryset = AttributeGroup.objects.all()
    serializer_class = AttributeGroupSerializer
    filterset_class = AttributeGroupFilter


class AttributeGroupDetails(SquestRetrieveUpdateDestroyAPIView):
    queryset = AttributeGroup.objects.all()
    serializer_class = AttributeGroupSerializer
