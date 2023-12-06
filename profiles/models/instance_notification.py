from django.db.models import CASCADE, ForeignKey, JSONField
from django.urls import reverse_lazy

from Squest.utils.ansible_when import AnsibleWhen
from profiles.models.notification_filter import NotificationFilter


class InstanceNotification(NotificationFilter):
    profile = ForeignKey(
        "profiles.Profile",
        blank=False,
        null=False,
        on_delete=CASCADE,
        related_name="instance_notification_filters",
        related_query_name="instance_notification_filter",
    )
    instance_states = JSONField(default=list, blank=True)

    def is_authorized(self, instance):
        if self.instance_states and instance.state not in self.instance_states:
            return False
        if self.services.exists() and instance.service not in self.services.all():
            return False

        if self.when and not self.when_render(instance):
            return False

        return True

    def when_render(self, instance):
        from service_catalog.api.serializers import InstanceSerializer
        context = {
            "instance": InstanceSerializer(instance).data
        }
        return AnsibleWhen.when_render(context=context, when_string=self.when)

    def get_absolute_url(self):
        return f"{reverse_lazy('profiles:profile')}#instance-notifications"
