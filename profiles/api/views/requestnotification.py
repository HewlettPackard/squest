from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from Squest.utils.squest_api_views import SquestGenericAPIView, SquestBrowsableAPIRenderer
from profiles.api.serializers.request_notification_filter_serializer import RequestNotificationFilterSerializer
from profiles.filters.notification_filter_filter import RequestNotificationFilterFilter
from profiles.models import RequestNotification


class RequestNotificationFilterDetails(RetrieveUpdateDestroyAPIView, SquestGenericAPIView, SquestBrowsableAPIRenderer):
    serializer_class = RequestNotificationFilterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RequestNotification.objects.filter(profile=self.request.user.profile)


class RequestNotificationFilterListCreate(ListCreateAPIView, SquestGenericAPIView, SquestBrowsableAPIRenderer):
    filterset_class = RequestNotificationFilterFilter
    serializer_class = RequestNotificationFilterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RequestNotification.objects.filter(profile=self.request.user.profile)
