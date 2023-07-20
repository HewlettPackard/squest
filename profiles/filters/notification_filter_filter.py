from Squest.utils.squest_filter import SquestFilter
from profiles.models import RequestNotification, InstanceNotification


class RequestNotificationFilterFilter(SquestFilter):
    class Meta:
        model = RequestNotification
        fields = ['name']


class InstanceNotificationFilterFilter(SquestFilter):
    class Meta:
        model = InstanceNotification
        fields = ['name']
