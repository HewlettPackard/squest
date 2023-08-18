from rest_framework.generics import get_object_or_404

from Squest.utils.squest_api_views import SquestListCreateAPIView, SquestRetrieveUpdateDestroyAPIView
from resource_tracker_v2.api.serializers.resource_serializer import ResourceSerializer
from resource_tracker_v2.filters.resource_filter import ResourceFilter
from resource_tracker_v2.models import Resource, ResourceGroup


class ResourceListCreate(SquestListCreateAPIView):
    serializer_class = ResourceSerializer
    filterset_class = ResourceFilter

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Resource.objects.none()
        return Resource.objects.filter(resource_group_id=self.kwargs['resource_group_id'])

    def get_serializer_context(self):
        context = super(ResourceListCreate, self).get_serializer_context()
        resource_group = get_object_or_404(ResourceGroup, pk=self.kwargs['resource_group_id'])
        context["resource_group"] = resource_group
        return context


class ResourceDetails(SquestRetrieveUpdateDestroyAPIView):
    serializer_class = ResourceSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Resource.objects.none()
        return Resource.objects.filter(resource_group_id=self.kwargs['resource_group_id'])

    def get_serializer_context(self):
        context = super(ResourceDetails, self).get_serializer_context()
        resource_group = get_object_or_404(ResourceGroup, pk=self.kwargs['resource_group_id'])
        context["resource_group"] = resource_group
        return context
