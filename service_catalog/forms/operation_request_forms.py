import urllib3
from django import forms
from service_catalog.forms.form_utils import FormUtils
from service_catalog.forms.utils import get_fields_from_survey
from service_catalog.models import Operation, Instance, Request, RequestMessage
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FIRST_BLOCK_FORM_FIELD_TITTLE = "1. Squest fields"
EXCLUDED_SURVEY_FIELDS = ["billing_group_id", "request_comment", "instance_name"]


class OperationRequestForm(forms.Form):

    request_comment = forms.CharField(label="Comment",
                                      help_text="Add a comment to your request",
                                      widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
                                      required=False)

    def __init__(self, user, *args, **kwargs):
        # get arguments from instance
        self.user = user
        operation_id = kwargs.pop('operation_id', None)
        instance_id = kwargs.pop('instance_id', None)
        super(OperationRequestForm, self).__init__(*args, **kwargs)

        self.operation = Operation.objects.get(id=operation_id)
        self.instance = Instance.objects.get(id=instance_id)

        # get all field that are not disabled by the admin
        purged_survey = FormUtils.get_available_fields(job_template_survey=self.operation.job_template.survey,
                                                       operation_survey=self.operation.tower_survey_fields)
        purged_survey_with_default = FormUtils.apply_spec_template_to_survey(job_template_survey=purged_survey,
                                                                             operation_survey=self.operation.tower_survey_fields,
                                                                             admin_spec=self.instance.spec,
                                                                             user_spec=self.instance.user_spec)
        purged_survey_with_validator = FormUtils.apply_user_validator_to_survey(
            job_template_survey=purged_survey_with_default,
            operation_survey=self.operation.tower_survey_fields)
        self.fields.update(get_fields_from_survey(purged_survey_with_validator, form_title="2. Operation fields"))
        self.fields['request_comment'].form_title = FIRST_BLOCK_FORM_FIELD_TITTLE

    def save(self):
        user_provided_survey_fields = dict()
        for field_key, value in self.cleaned_data.items():
            if field_key not in EXCLUDED_SURVEY_FIELDS:
                user_provided_survey_fields[field_key] = value
        new_request = Request.objects.create(instance=self.instance,
                                             operation=self.operation,
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
