from django.db import models
from django.db.models import CASCADE, ForeignKey, ManyToManyField, TextField, CharField
from django_mysql.models import ListCharField

from Squest.utils.ansible_when import AnsibleWhen


class NotificationFilter(models.Model):
    name = CharField(max_length=100)
    profile = ForeignKey(
        "profiles.Profile",
        blank=False,
        null=False,
        on_delete=CASCADE,
        related_name="notification_filters",
        related_query_name="notification_filter",
    )
    services = ManyToManyField(
        "service_catalog.Service",
        blank=True,
        related_name="notification_filters",
        related_query_name="notification_filter",
    )
    operations = ManyToManyField(
        "service_catalog.Operation",
        blank=True,
        related_name="notification_filters",
        related_query_name="notification_filter",
    )
    request_states = ListCharField(base_field=CharField(max_length=50),
                                   size=15,
                                   max_length=(15 * 50 + 14))
    # "E.G: request.instance.spec['configvar'] == 'value' and request.fill_in_survey['location'] == 'value'"
    when = TextField(blank=True, null=True,
                     help_text="Ansible like 'when' with `request` as context. No Jinja brackets needed")

    def is_authorized(self, request=None):
        if request:
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
            "request": RequestSerializer(request).data
        }
        return AnsibleWhen.when_render(context=context, when_string=self.when)
