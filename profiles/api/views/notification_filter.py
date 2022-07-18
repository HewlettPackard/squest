from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.permissions import IsAdminUser

from profiles.api.serializers.notification_filter_serializer import NotificationFilterSerializer
from profiles.filters.notification_filter_filter import NotificationFilterFilter
from profiles.models import NotificationFilter


class NotificationFilterDetails(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = NotificationFilterSerializer

    def get_queryset(self):
        return NotificationFilter.objects.filter(profile=self.request.user.profile)


class NotificationFilterListCreate(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    filterset_class = NotificationFilterFilter
    serializer_class = NotificationFilterSerializer

    def get_queryset(self):
        return NotificationFilter.objects.filter(profile=self.request.user.profile)
