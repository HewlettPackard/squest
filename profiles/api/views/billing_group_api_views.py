from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser

from profiles.api.serializers.billing_group_serializers import BillingGroupSerializer
from profiles.models import BillingGroup


class BillingGroupDetails(RetrieveUpdateDestroyAPIView):
    serializer_class = BillingGroupSerializer
    permission_classes = [IsAdminUser]
    queryset = BillingGroup.objects.all()


class BillingGroupListCreate(ListCreateAPIView):
    serializer_class = BillingGroupSerializer
    permission_classes = [IsAdminUser]
    queryset = BillingGroup.objects.all()
