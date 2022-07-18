from profiles.models import NotificationFilter
from Squest.utils.squest_filter import SquestFilter


class NotificationFilterFilter(SquestFilter):
    class Meta:
        model = NotificationFilter
        fields = ['name']
