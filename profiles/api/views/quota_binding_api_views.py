from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser

from profiles.api.serializers.quota_binding_serializers import QuotaBindingSerializer, QuotaBindingWriteSerializer
from profiles.models import QuotaBinding


class QuotaBindingDetails(RetrieveUpdateDestroyAPIView):
    serializer_class = QuotaBindingSerializer
    permission_classes = [IsAdminUser]
    queryset = QuotaBinding.objects.all()

    def put(self, request, *args, **kwargs):
        self.serializer_class = QuotaBindingWriteSerializer
        return super(QuotaBindingDetails, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.serializer_class = QuotaBindingWriteSerializer
        return super(QuotaBindingDetails, self).patch(request, *args, **kwargs)


class QuotaBindingListCreate(ListCreateAPIView):
    serializer_class = QuotaBindingSerializer
    permission_classes = [IsAdminUser]
    queryset = QuotaBinding.objects.all()

    def create(self, request, *args, **kwargs):
        self.serializer_class = QuotaBindingWriteSerializer
        return super(QuotaBindingListCreate, self).create(request, *args, **kwargs)
