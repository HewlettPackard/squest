from django import forms

from Squest.utils.squest_form import SquestForm
from Squest.utils.squest_model_form import SquestModelForm
from profiles.models.scope import Scope
from service_catalog.forms.form_generator import FormGenerator
from service_catalog.models import Instance, Request, RequestMessage


class ServiceInstanceForm(SquestModelForm):
    class Meta:
        model = Instance
        fields = ['name', 'quota_scope']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.operation = kwargs.pop('operation', None)
        super(ServiceInstanceForm, self).__init__(*args, **kwargs)
        quota_scopes = Scope.get_queryset_for_user(self.user, 'profiles.consume_quota_scope')
        self.fields['quota_scope'].queryset = quota_scopes
        if quota_scopes.count() == 0:
            self.fields['quota_scope'].help_text =  'Permission "profiles.consume_quota_scope needed" to choose your scope.'
        if quota_scopes.count() == 1:
            self.fields['quota_scope'].initial =  quota_scopes.first()
    def save(self, commit=True):
        squest_instance = super().save(False)
        squest_instance.service = self.operation.service
        squest_instance.requester = self.user
        squest_instance.save()
        return squest_instance


class ServiceRequestForm(SquestForm):
    request_comment = forms.CharField(label="Comment",
                                      help_text="Add a comment to your request",
                                      required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.operation = kwargs.pop('operation', None)
        self.quota_scope = kwargs.pop('quota_scope', None)
        super(ServiceRequestForm, self).__init__(*args, **kwargs)

        form_generator = FormGenerator(operation=self.operation, quota_scope=self.quota_scope)
        self.fields.update(form_generator.generate_form())

    def save(self, squest_instance):
        comment = self.cleaned_data.pop("request_comment")
        user_provided_survey_fields = dict()
        for field_key, value in self.cleaned_data.items():
            user_provided_survey_fields[field_key] = value

        # create the request
        new_request = Request.objects.create(instance=squest_instance,
                                             operation=self.operation,
                                             fill_in_survey=user_provided_survey_fields,
                                             user=self.user)

        # save the comment
        message = None
        if comment is not None and comment != "":
            message = RequestMessage.objects.create(request=new_request, sender=self.user, content=comment)

        # send notification
        from service_catalog.mail_utils import send_mail_request_update
        send_mail_request_update(target_request=new_request, user_applied_state=self.user, message=message)
        return new_request
