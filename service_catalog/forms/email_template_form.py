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

        limit_users = self.email_template.get_list_concerned_user()

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

    def save(self):
        user_id_list = self.cleaned_data.get('users')
        logger.info(
            f"Sending email template name '{self.email_template.name}' to users: '{self.cleaned_data.get('users')}'")
        send_template_email(self.email_template, user_id_list)
