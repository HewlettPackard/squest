import copy

from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from Squest.utils.squest_api_views import SquestRetrieveUpdateDestroyAPIView, SquestListCreateAPIView
from resource_tracker_v2.api.serializers.transformer_serializer import TransformerSerializer
from resource_tracker_v2.filters.transformer_filter import TransformerFilter
from resource_tracker_v2.models import Transformer, ResourceGroup


class TransformerListCreate(SquestListCreateAPIView):
    serializer_class = TransformerSerializer
    filterset_class = TransformerFilter

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Transformer.objects.none()
        return Transformer.objects.filter(resource_group_id=self.kwargs['resource_group_id'])

    def create(self, request, **kwargs):
        resource_group_id = self.kwargs['resource_group_id']
        resource_group = get_object_or_404(ResourceGroup, pk=resource_group_id)
        data = copy.copy(request.data)
        data["resource_group"] = resource_group.id
        serializer = TransformerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class TransformerDetails(SquestRetrieveUpdateDestroyAPIView):
    serializer_class = TransformerSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Transformer.objects.none()
        return Transformer.objects.filter(resource_group_id=self.kwargs['resource_group_id'])

    def get_serializer(self, *args, **kwargs):
        updated_kwargs = copy.deepcopy(kwargs)
        if 'data' in kwargs:
            updated_kwargs['data']['resource_group'] = self.kwargs.get('resource_group_id', None)
        serializer = super(TransformerDetails, self).get_serializer(*args, **updated_kwargs)
        serializer.context["resource_group"] = self.kwargs.get('resource_group_id', None)
        return serializer
