from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from Squest.utils.squest_api_views import SquestGenericAPIView, SquestBrowsableAPIRenderer
from profiles.api.serializers.support_notification_filter_serializer import InstanceNotificationFilterSerializer
from profiles.filters.notification_filter_filter import InstanceNotificationFilterFilter
from profiles.models import InstanceNotification


class InstanceNotificationFilterDetails(RetrieveUpdateDestroyAPIView, SquestGenericAPIView, SquestBrowsableAPIRenderer):
    serializer_class = InstanceNotificationFilterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return InstanceNotification.objects.filter(profile=self.request.user.profile)


class InstanceNotificationFilterListCreate(ListCreateAPIView, SquestGenericAPIView, SquestBrowsableAPIRenderer):
    filterset_class = InstanceNotificationFilterFilter
    serializer_class = InstanceNotificationFilterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return InstanceNotification.objects.filter(profile=self.request.user.profile)
