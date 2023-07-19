from Squest.utils.squest_api_views import SquestRetrieveUpdateDestroyAPIView, SquestListCreateAPIView
from profiles.api.serializers.request_notification_filter_serializer import RequestNotificationFilterSerializer
from profiles.filters.notification_filter_filter import RequestNotificationFilterFilter
from profiles.models import RequestNotification


class RequestNotificationFilterDetails(SquestRetrieveUpdateDestroyAPIView):
    serializer_class = RequestNotificationFilterSerializer

    def get_queryset(self):
        return RequestNotification.objects.filter(profile=self.request.user.profile)


class RequestNotificationFilterListCreate(SquestListCreateAPIView):
    filterset_class = RequestNotificationFilterFilter
    serializer_class = RequestNotificationFilterSerializer

    def get_queryset(self):
        return RequestNotification.objects.filter(profile=self.request.user.profile)
