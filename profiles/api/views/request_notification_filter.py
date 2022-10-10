from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.permissions import IsAdminUser

from profiles.api.serializers.request_notification_filter_serializer import RequestNotificationFilterSerializer
from profiles.filters.notification_filter_filter import RequestNotificationFilterFilter
from profiles.models import RequestNotification


class RequestNotificationFilterDetails(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = RequestNotificationFilterSerializer

    def get_queryset(self):
        return RequestNotification.objects.filter(profile=self.request.user.profile)


class RequestNotificationFilterListCreate(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    filterset_class = RequestNotificationFilterFilter
    serializer_class = RequestNotificationFilterSerializer

    def get_queryset(self):
        return RequestNotification.objects.filter(profile=self.request.user.profile)
