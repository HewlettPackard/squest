from django import forms

from Squest.utils.squest_form import SquestForm
from profiles.models.scope import Scope
from service_catalog.forms.form_generator import FormGenerator

FIRST_BLOCK_FORM_FIELD_TITTLE = "1. Squest fields"
EXCLUDED_SURVEY_FIELDS = ["quota_scope", "request_comment", "squest_instance_name"]


class ServiceRequestForm1(SquestForm):
    squest_instance_name = forms.CharField(label="Squest instance name",
                                           help_text="Ideally a short name like 'my-service-01'",
                                           )
    quota_scope = forms.ModelChoiceField(
        label="Quota",
        queryset=Scope.objects.none(),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ServiceRequestForm1, self).__init__(*args, **kwargs)
        self.fields['quota_scope'].queryset = Scope.get_queryset_for_user(user, 'profiles.consume_quota_scope')


class ServiceRequestForm2(SquestForm):
    request_comment = forms.CharField(label="Comment",
                                      help_text="Add a comment to your request",
                                      required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.service = kwargs.pop('service', None)
        self.create_operation = kwargs.pop('operation', None)
        self.squest_instance_name = kwargs.pop('squest_instance_name', None)
        self.quota_scope = kwargs.pop('quota_scope', None)
        super(ServiceRequestForm2, self).__init__(*args, **kwargs)

        form_generator = FormGenerator(operation=self.create_operation)
        self.fields.update(form_generator.generate_form())
