from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.permissions import IsAdminUser

from profiles.api.serializers.support_notification_filter_serializer import SupportNotificationFilterSerializer
from profiles.filters.notification_filter_filter import InstanceNotificationFilterFilter
from profiles.models import InstanceNotification


class SupportNotificationFilterDetails(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = SupportNotificationFilterSerializer

    def get_queryset(self):
        return InstanceNotification.objects.filter(profile=self.request.user.profile)


class SupportNotificationFilterListCreate(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    filterset_class = InstanceNotificationFilterFilter
    serializer_class = SupportNotificationFilterSerializer

    def get_queryset(self):
        return InstanceNotification.objects.filter(profile=self.request.user.profile)
