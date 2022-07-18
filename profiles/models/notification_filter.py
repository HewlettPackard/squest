from django.db import models
from django.db.models import CASCADE, ForeignKey, ManyToManyField, TextField, CharField
from django_mysql.models import ListCharField
from jinja2 import Template, UndefinedError


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
    instance_states = ListCharField(base_field=CharField(max_length=50),
                                    size=15,
                                    max_length=(15 * 50 + 14))
    when = TextField(blank=True, null=True)  # "E.G: spec['configvar'] == 'value' and user_spec['other'] == 'value'"

    def is_authorized(self, instance=None, request=None):
        if request:
            if self.request_states and request.state not in self.request_states:
                return False
            if self.operations.exists() and request.operation not in self.operations.all():
                return False

        if instance:
            if self.services.exists() and instance.service not in self.services.all():
                return False
            if self.instance_states and instance.state not in self.instance_states:
                return False
            if self.when and not self.when_render(instance):
                return False
        return True

    def when_render(self, instance):
        context = {
            "spec": instance.spec,
            "user_spec": instance.user_spec
        }
        template_string = "{% if " + self.when + " %}True{% else %}{% endif %}"
        template = Template(template_string)
        try:
            template_rendered = template.render(context)
            return bool(template_rendered)
        except UndefinedError:
            # in case of any error we just use the given URL with the jinja so the admin can see the templating error
            return False
