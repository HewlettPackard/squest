import copy

from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from Squest.utils.squest_api_views import SquestListCreateAPIView, SquestRetrieveUpdateDestroyAPIView
from profiles.api.serializers.quata_serializer import QuotaSerializer, QuotaReadSerializer
from profiles.models import Quota, Scope


class QuotaListCreateView(SquestListCreateAPIView):
    serializer_class = QuotaReadSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Quota.objects.none()
        scope_id = self.kwargs['scope_id']
        return Quota.objects.filter(scope_id=scope_id)

    def create(self, request, **kwargs):
        scope_id = self.kwargs['scope_id']
        scope = get_object_or_404(Scope, pk=scope_id)
        data = copy.copy(request.data)
        data["scope"] = scope.id
        serializer = QuotaSerializer(data=data)
        if serializer.is_valid():
            new_quota = serializer.save()
            read_serializer = QuotaReadSerializer(instance=new_quota)
            return Response(read_serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class QuotaDetails(SquestRetrieveUpdateDestroyAPIView):
    serializer_class = QuotaReadSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Quota.objects.none()
        scope_id = self.kwargs['scope_id']
        queryset = Quota.objects.filter(scope_id=scope_id)
        return queryset

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            kwargs['data']['scope'] = self.kwargs.get('scope_id', None)
        serializer = super(QuotaDetails, self).get_serializer(*args, **kwargs)
        serializer.context["scope"] = self.kwargs.get('scope_id', None)
        return serializer

    def get_object(self):
        scope_id = self.kwargs.get('scope_id')
        quota_id = self.kwargs.get('pk')
        quota = get_object_or_404(Quota, id=quota_id, scope_id=scope_id)
        return quota