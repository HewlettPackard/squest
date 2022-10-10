from profiles.models import RequestNotification, InstanceNotification
from Squest.utils.squest_filter import SquestFilter


class RequestNotificationFilterFilter(SquestFilter):
    class Meta:
        model = RequestNotification
        fields = ['name']


class InstanceNotificationFilterFilter(SquestFilter):
    class Meta:
        model = InstanceNotification
        fields = ['name']
