import logging

from django.contrib.auth.models import User
from django.forms import TypedMultipleChoiceField, SelectMultiple

from Squest.utils.ansible_when import AnsibleWhen
from Squest.utils.squest_form import SquestForm
from Squest.utils.squest_model_form import SquestModelForm
from profiles.models import Scope
from service_catalog.mail_utils import send_template_email
from service_catalog.models import EmailTemplate, InstanceState, Service, Instance

logger = logging.getLogger(__name__)


class EmailTemplateForm(SquestModelForm):
    instance_states = TypedMultipleChoiceField(label="Instance states",
                                               coerce=int,
                                               required=False,
                                               choices=InstanceState.choices,
                                               widget=SelectMultiple(attrs={'class': 'form-control'}))

    class Meta:
        model = EmailTemplate
        fields = ["name", "email_title", "html_content", "services", "instance_states", "quota_scopes", "when"]


class EmailTemplateSendForm(SquestForm):

    def __init__(self, *args, **kwargs):
        self.email_template = kwargs.pop("email_template")
        super(EmailTemplateSendForm, self).__init__(*args, **kwargs)

        qs_service = Service.objects.all()
        if self.email_template.services.count() > 0:
            qs_service = self.email_template.services.all()

        instance_states = [item[0] for item in InstanceState.choices]
        if self.email_template.instance_states:
            instance_states = self.email_template.instance_states

        qs_quota_scopes = Scope.objects.all()
        if self.email_template.quota_scopes.count() > 0:
            qs_quota_scopes = self.email_template.quota_scopes.all()

        qs_instance = Instance.objects.filter(service__in=qs_service,
                                              state__in=instance_states,
                                              quota_scope__in=qs_quota_scopes)

        if self.email_template.when:
            for instance in qs_instance.all():
                if not self.when_render(self.email_template.when, instance):
                    qs_instance = qs_instance.exclude(id=instance.id)

        limit_users = User.objects.filter(instance__in=qs_instance).distinct()

        self.fields["users"] = TypedMultipleChoiceField(
            label="User emails",
            coerce=int,
            required=True,
            choices=User.objects.all().values_list("id", "username"),
            initial=list(limit_users.values_list("id", flat=True)),
            help_text=f"User emails",
            widget=SelectMultiple(
                attrs={'class': 'form-control selectpicker', 'data-live-search': 'true'})
        )

    @staticmethod
    def when_render(when, instance):
        from service_catalog.api.serializers import InstanceSerializer
        context = {
            "instance": InstanceSerializer(instance).data
        }
        return AnsibleWhen.when_render(context=context, when_string=when)

    def save(self):
        user_id_list = self.cleaned_data.get('users')
        logger.info(
            f"Sending email template name '{self.email_template.name}' to users: '{self.cleaned_data.get('users')}'")
        send_template_email(self.email_template, user_id_list)
