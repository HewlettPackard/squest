from django.contrib.auth.models import User
from django.db.models import CharField, TextField, SET_NULL, ForeignKey, ManyToManyField, JSONField

from Squest.utils.ansible_when import AnsibleWhen
from Squest.utils.squest_model import SquestModel
from profiles.models import Scope
from service_catalog.models import Service, InstanceState, Instance


class EmailTemplate(SquestModel):

    class Meta:
        permissions = [
            ("send_email_template", "Can send email template"),
        ]
        default_permissions = ('add', 'change', 'delete', 'view', 'list')

    name = CharField(max_length=100)
    email_title = CharField(max_length=255, blank=False, null=False)
    html_content = TextField(blank=False, null=False)

    services = ManyToManyField(
        Service,
        blank=True,
        help_text="Filter on services. Nothing selected means all services impacted by the email",
        related_name="email_templates",
        related_query_name="email_template",
    )

    # list of InstanceState.
    instance_states = JSONField(default=list, blank=True,
                                help_text="Filter instance state. Nothing selected means all state impacted by the email")

    quota_scopes = ManyToManyField(
        Scope,
        blank=True,
        help_text="Filter on quota scope. Nothing selected means all quota scope impacted by the email",
        related_name="email_templates",
        related_query_name="email_template",
    )

    when = CharField(max_length=2000, blank=True, null=True,
                     help_text="Ansible like 'when' with `instance` as context. No Jinja brackets needed")

    def __str__(self):
        return self.name

    def get_list_concerned_user(self):
        qs_service = Service.objects.all()
        if self.services.count() > 0:
            qs_service = self.services.all()

        instance_states = [item[0] for item in InstanceState.choices]
        if self.instance_states:
            instance_states = self.instance_states

        qs_quota_scopes = Scope.objects.all()
        if self.quota_scopes.count() > 0:
            qs_quota_scopes = self.quota_scopes.all()

        qs_instance = Instance.objects.filter(service__in=qs_service,
                                              state__in=instance_states,
                                              quota_scope__in=qs_quota_scopes)

        if self.when:
            for instance in qs_instance.all():
                if not self.when_render(self.when, instance):
                    qs_instance = qs_instance.exclude(id=instance.id)

        return User.objects.filter(instance__in=qs_instance).distinct()

    @staticmethod
    def when_render(when, instance):
        from service_catalog.api.serializers import InstanceSerializer
        context = {
            "instance": InstanceSerializer(instance).data
        }
        return AnsibleWhen.when_render(context=context, when_string=when)
