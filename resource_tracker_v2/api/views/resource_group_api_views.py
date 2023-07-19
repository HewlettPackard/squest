from Squest.utils.squest_api_views import SquestListCreateAPIView, SquestRetrieveUpdateDestroyAPIView
from resource_tracker_v2.api.serializers.resource_group_serializers import ResourceGroupSerializer
from resource_tracker_v2.filters.resource_group_filter import ResourceGroupFilter
from resource_tracker_v2.models import ResourceGroup


class ResourceGroupList(SquestListCreateAPIView):
    queryset = ResourceGroup.objects.all()
    serializer_class = ResourceGroupSerializer
    filterset_class = ResourceGroupFilter


class ResourceGroupDetails(SquestRetrieveUpdateDestroyAPIView):
    queryset = ResourceGroup.objects.all()
    serializer_class = ResourceGroupSerializer
