from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from resource_tracker_v2.api.serializers.transformer_serializer import TransformerSerializer
from resource_tracker_v2.filters.transformer_filter import TransformerFilter
from resource_tracker_v2.models import Transformer, ResourceGroup


class TransformerListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = TransformerSerializer
    filterset_class = TransformerFilter

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Transformer.objects.none()
        resource_group_id = self.kwargs['resource_group_id']
        queryset = Transformer.objects.filter(resource_group_id=resource_group_id)
        return queryset

    def create(self, request, **kwargs):
        resource_group_id = self.kwargs['resource_group_id']
        resource_group = get_object_or_404(ResourceGroup, pk=resource_group_id)
        context = {'resource_group': resource_group}
        serializer = TransformerSerializer(data=request.data, context=context)
        if serializer.is_valid():
            new_transformer = serializer.save()
            # read_serializer = TransformerSerializer(instance=new_transformer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransformerDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = TransformerSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Transformer.objects.none()
        resource_group_id = self.kwargs['resource_group_id']
        queryset = Transformer.objects.filter(resource_group_id=resource_group_id)
        return queryset

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            kwargs['data']['resource_group'] = self.kwargs.get('resource_group_id', None)
        serializer = super(TransformerDetails, self).get_serializer(*args, **kwargs)
        serializer.context["resource_group"] = self.kwargs.get('resource_group_id', None)
        return serializer

    def get_object(self):
        resource_group_id = self.kwargs.get('resource_group_id')
        transformer_id = self.kwargs.get('pk')
        resource = get_object_or_404(Transformer, id=transformer_id, resource_group_id=resource_group_id)
        return resource
