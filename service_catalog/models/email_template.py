from django.contrib.auth.models import User
from django.db.models import CharField, TextField, SET_NULL, ForeignKey, ManyToManyField, JSONField

from Squest.utils.squest_model import SquestModel
from profiles.models import Scope
from service_catalog.models import Service


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
