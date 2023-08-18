import copy

from rest_framework.generics import get_object_or_404

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

    def get_serializer_context(self):
        context = super(TransformerListCreate, self).get_serializer_context()
        resource_group = get_object_or_404(ResourceGroup, pk=self.kwargs['resource_group_id'])
        context["resource_group"] = resource_group
        return context


class TransformerDetails(SquestRetrieveUpdateDestroyAPIView):
    serializer_class = TransformerSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Transformer.objects.none()
        return Transformer.objects.filter(resource_group_id=self.kwargs['resource_group_id'])

    def get_serializer_context(self):
        context = super(TransformerDetails, self).get_serializer_context()
        resource_group = get_object_or_404(ResourceGroup, pk=self.kwargs['resource_group_id'])
        context["resource_group"] = resource_group
        return context

    def get_serializer(self, *args, **kwargs):
        updated_kwargs = copy.deepcopy(kwargs)
        if 'data' in kwargs:
            updated_kwargs['data']['resource_group'] = self.kwargs.get('resource_group_id', None)
        serializer = super(TransformerDetails, self).get_serializer(*args, **updated_kwargs)
        serializer.context["resource_group"] = self.kwargs.get('resource_group_id', None)
        return serializer
