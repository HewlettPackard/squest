from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser

from profiles.api.serializers.billing_group_serializers import BillingGroupReadSerializer, BillingGroupSerializer
from profiles.models import BillingGroup


class BillingGroupDetails(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = BillingGroup.objects.all()

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return BillingGroupSerializer
        return BillingGroupReadSerializer


class BillingGroupListCreate(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = BillingGroup.objects.all()

    def get_serializer_class(self):
        if self.request.method in ["POST"]:
            return BillingGroupSerializer
        return BillingGroupReadSerializer
