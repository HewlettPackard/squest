from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView

from Squest.utils.squest_api_views import SquestRetrieveUpdateDestroyAPIView, SquestListCreateAPIView
from profiles.api.serializers.support_notification_filter_serializer import SupportNotificationFilterSerializer
from profiles.filters.notification_filter_filter import InstanceNotificationFilterFilter
from profiles.models import InstanceNotification


class SupportNotificationFilterDetails(SquestRetrieveUpdateDestroyAPIView):
    serializer_class = SupportNotificationFilterSerializer

    def get_queryset(self):
        return InstanceNotification.objects.filter(profile=self.request.user.profile)


class SupportNotificationFilterListCreate(SquestListCreateAPIView):
    filterset_class = InstanceNotificationFilterFilter
    serializer_class = SupportNotificationFilterSerializer

    def get_queryset(self):
        return InstanceNotification.objects.filter(profile=self.request.user.profile)
