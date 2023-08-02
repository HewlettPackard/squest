from django import forms

from Squest.utils.squest_form import SquestForm
from Squest.utils.squest_model_form import SquestModelForm
from profiles.models.scope import Scope
from service_catalog.forms.form_generator import FormGenerator
from service_catalog.models import Instance


class ServiceInstanceForm(SquestModelForm):
    class Meta:
        model = Instance
        fields = ['name', 'quota_scope']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.service = kwargs.pop('service', None)
        super(ServiceInstanceForm, self).__init__(*args, **kwargs)
        self.fields['quota_scope'].queryset = Scope.get_queryset_for_user(self.user, 'profiles.consume_quota_scope')

    def save(self, commit=True):
        squest_instance = super().save(False)
        squest_instance.service = self.service
        squest_instance.requester = self.user
        squest_instance.save()
        return squest_instance


class ServiceRequestForm(SquestForm):
    request_comment = forms.CharField(label="Comment",
                                      help_text="Add a comment to your request",
                                      required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.service = kwargs.pop('service', None)
        self.create_operation = kwargs.pop('operation', None)
        self.quota_scope = kwargs.pop('quota_scope', None)
        super(ServiceRequestForm, self).__init__(*args, **kwargs)

        form_generator = FormGenerator(operation=self.create_operation, quota_scope=self.quota_scope)
        self.fields.update(form_generator.generate_form())
