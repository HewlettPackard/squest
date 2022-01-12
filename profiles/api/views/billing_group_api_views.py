from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser

from profiles.api.serializers.billing_group_serializers import BillingGroupSerializer, BillingGroupWriteSerializer
from profiles.models import BillingGroup


class BillingGroupDetails(RetrieveUpdateDestroyAPIView):
    serializer_class = BillingGroupSerializer
    permission_classes = [IsAdminUser]
    queryset = BillingGroup.objects.all()

    def put(self, request, *args, **kwargs):
        self.serializer_class = BillingGroupWriteSerializer
        return super(BillingGroupDetails, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.serializer_class = BillingGroupWriteSerializer
        return super(BillingGroupDetails, self).patch(request, *args, **kwargs)


class BillingGroupListCreate(ListCreateAPIView):
    serializer_class = BillingGroupSerializer
    permission_classes = [IsAdminUser]
    queryset = BillingGroup.objects.all()

    def create(self, request, *args, **kwargs):
        self.serializer_class = BillingGroupWriteSerializer
        return super(BillingGroupListCreate, self).create(request, *args, **kwargs)
