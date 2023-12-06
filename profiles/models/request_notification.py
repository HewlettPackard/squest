from django.db.models import CASCADE, ForeignKey, ManyToManyField, JSONField
from django.urls import reverse_lazy

from Squest.utils.ansible_when import AnsibleWhen
from profiles.models.notification_filter import NotificationFilter


class RequestNotification(NotificationFilter):
    profile = ForeignKey(
        "profiles.Profile",
        blank=False,
        null=False,
        on_delete=CASCADE,
        related_name="request_notification_filters",
        related_query_name="request_notification_filter",
    )
    request_states = JSONField(default=list, blank=True)
    operations = ManyToManyField(
        "service_catalog.Operation",
        blank=True,
        related_name="request_notification_filters",
        related_query_name="request_notification_filter",
    )

    def is_authorized(self, request):
        if self.request_states and request.state not in self.request_states:
            return False
        if self.operations.exists() and request.operation not in self.operations.all():
            return False
        if self.services.exists() and request.instance.service not in self.services.all():
            return False

        if self.when and not self.when_render(request):
            return False

        return True

    def when_render(self, request):
        from service_catalog.api.serializers import RequestSerializer
        context = {
            "request": RequestSerializer(request).data,
        }
        return AnsibleWhen.when_render(context=context, when_string=self.when)

    def get_absolute_url(self):
        return f"{reverse_lazy('profiles:profile')}#request-notifications"
