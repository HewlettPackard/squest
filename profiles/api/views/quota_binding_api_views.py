from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser

from profiles.api.serializers.quota_binding_serializers import QuotaBindingReadSerializer, QuotaBindingSerializer
from profiles.filters.quota_binding_filter import QuotaBindingFilter
from profiles.models import QuotaBinding


class QuotaBindingDetails(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = QuotaBinding.objects.all()

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return QuotaBindingSerializer
        return QuotaBindingReadSerializer


class QuotaBindingListCreate(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = QuotaBinding.objects.all()
    filterset_class = QuotaBindingFilter

    def get_serializer_class(self):
        if self.request.method in ["POST"]:
            return QuotaBindingSerializer
        return QuotaBindingReadSerializer
