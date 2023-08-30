from Squest.utils.squest_api_views import SquestListCreateAPIView, SquestRetrieveUpdateDestroyAPIView
from resource_tracker_v2.api.serializers.resource_serializer import ResourceSerializer
from resource_tracker_v2.filters.resource_filter import ResourceFilter
from resource_tracker_v2.models import Resource


class ResourceListCreate(SquestListCreateAPIView):
    serializer_class = ResourceSerializer
    filterset_class = ResourceFilter
    queryset = Resource.objects.all()


class ResourceDetails(SquestRetrieveUpdateDestroyAPIView):
    serializer_class = ResourceSerializer
    queryset = Resource.objects.all()
