from django.db.models import CASCADE, ForeignKey, CharField
from django_mysql.models import ListCharField

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
    instance_states = ListCharField(base_field=CharField(max_length=50),
                                    size=15,
                                    max_length=(15 * 50 + 14))

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
