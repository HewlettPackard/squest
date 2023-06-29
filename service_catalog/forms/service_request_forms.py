
import urllib3
from django import forms
from django.core.exceptions import ValidationError

from profiles.models.scope import Scope
from service_catalog.forms.form_utils import FormUtils
from service_catalog.forms.utils import get_fields_from_survey
from service_catalog.models import Service, Operation, Instance, Request, RequestMessage

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FIRST_BLOCK_FORM_FIELD_TITTLE = "1. Squest fields"
EXCLUDED_SURVEY_FIELDS = ["quota_scope_id", "request_comment", "squest_instance_name"]


class ServiceRequestForm(forms.Form):
    squest_instance_name = forms.CharField(label="Squest instance name",
                                           help_text="Help to identify the requested service in the 'Instances' view",
                                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    request_comment = forms.CharField(label="Comment",
                                      help_text="Add a comment to your request",
                                      widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
                                      required=False)

    quota_scope = forms.ModelChoiceField(
            label="Scope",
            queryset=Scope.objects.none(),
            required=True,
            widget=forms.Select(attrs={"class": "form-control selectpicker", "data-live-search": "true"})
        )

    def __init__(self, user, *args, **kwargs):
        # get arguments from instance
        self.user = user
        service_id = kwargs.pop('service_id', None)
        operation_id = kwargs.pop('operation_id', None)
        super(ServiceRequestForm, self).__init__(*args, **kwargs)
        self.service = Service.objects.get(id=service_id)
        self.create_operation = Operation.objects.get(id=operation_id)
        self.fields['quota_scope'].queryset = Scope.objects.filter() #TODO get_queryset_for_user with consume_quota

        # get all field that are not disabled by the admin
        purged_survey = FormUtils.get_available_fields(job_template_survey=self.create_operation.job_template.survey,
                                                       operation_survey=self.create_operation.tower_survey_fields)
        purged_survey_with_default = FormUtils.apply_jinja_template_to_survey(job_template_survey=purged_survey,
                                                                              operation_survey=self.create_operation.tower_survey_fields)
        purged_survey_with_validator = FormUtils.apply_user_validator_to_survey(job_template_survey=purged_survey_with_default,
                                                                                operation_survey=self.create_operation.tower_survey_fields)
        self.fields.update(get_fields_from_survey(purged_survey_with_validator))
        self.fields['squest_instance_name'].form_title = FIRST_BLOCK_FORM_FIELD_TITTLE

    def save(self):
        user_provided_survey_fields = dict()
        for field_key, value in self.cleaned_data.items():
            if field_key not in EXCLUDED_SURVEY_FIELDS:
                user_provided_survey_fields[field_key] = value
        # create the instance
        instance_name = self.cleaned_data["squest_instance_name"]
        quota_scope = self.cleaned_data["quota_scope"]
        new_instance = Instance.objects.create(service=self.service, name=instance_name, quota_scope=quota_scope,
                                               requester=self.user)
        # create the request
        new_request = Request.objects.create(instance=new_instance,
                                             operation=self.create_operation,
                                             fill_in_survey=user_provided_survey_fields,
                                             user=self.user)

        # save the comment
        request_comment = self.cleaned_data["request_comment"] if self.cleaned_data["request_comment"] else None
        message = None
        if request_comment is not None:
            message = RequestMessage.objects.create(request=new_request, sender=self.user, content=request_comment)
        from service_catalog.mail_utils import send_mail_request_update
        send_mail_request_update(target_request=new_request, user_applied_state=new_request.user, message=message)
        return new_request

    def clean(self):
        super(ServiceRequestForm, self).clean()
