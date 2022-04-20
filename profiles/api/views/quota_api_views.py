from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser

from profiles.api.serializers.quota_serializers import QuotaSerializer
from profiles.filters.quota_filter import QuotaFilter
from profiles.models import Quota


class QuotaDetails(RetrieveUpdateDestroyAPIView):
    serializer_class = QuotaSerializer
    permission_classes = [IsAdminUser]
    queryset = Quota.objects.all()


class QuotaListCreate(ListCreateAPIView):
    serializer_class = QuotaSerializer
    permission_classes = [IsAdminUser]
    queryset = Quota.objects.all()
    filterset_class = QuotaFilter
