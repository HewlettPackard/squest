import copy

from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from Squest.utils.squest_api_views import SquestListCreateAPIView, SquestRetrieveUpdateDestroyAPIView
from resource_tracker_v2.api.serializers.resource_serializer import ResourceSerializer, ResourceCreateSerializer
from resource_tracker_v2.filters.resource_filter import ResourceFilter
from resource_tracker_v2.models import Resource, ResourceGroup


class ResourceListCreate(SquestListCreateAPIView):
    serializer_class = ResourceSerializer
    filterset_class = ResourceFilter

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Resource.objects.none()
        return Resource.objects.filter(resource_group_id=self.kwargs['resource_group_id'])

    def create(self, request, **kwargs):
        resource_group_id = self.kwargs['resource_group_id']
        resource_group = get_object_or_404(ResourceGroup, pk=resource_group_id)
        data = copy.copy(request.data)
        data["resource_group"] = resource_group.id
        serializer = ResourceCreateSerializer(data=data)
        if serializer.is_valid():
            new_resource = serializer.save()
            read_serializer = ResourceSerializer(instance=new_resource)
            return Response(read_serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class ResourceDetails(SquestRetrieveUpdateDestroyAPIView):
    serializer_class = ResourceSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Resource.objects.none()
        return Resource.objects.filter(resource_group_id=self.kwargs['resource_group_id'])

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            if kwargs['data'].get('resource_group') is None:
                if hasattr(kwargs['data'], '_mutable'):
                    is_mutable = kwargs['data']._mutable
                    kwargs['data']._mutable = True
                kwargs['data']['resource_group'] = self.kwargs.get('resource_group_id', None)
                if hasattr(kwargs['data'], '_mutable'):
                    kwargs['data']._mutable = is_mutable
        serializer = super(ResourceDetails, self).get_serializer(*args, **kwargs)
        serializer.context["resource_group"] = self.kwargs.get('resource_group_id', None)
        return serializer
