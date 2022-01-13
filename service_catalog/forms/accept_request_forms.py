import urllib3
from django import forms
from service_catalog.forms.utils import get_fields_from_survey, prefill_form_with_user_values
from service_catalog.models import Request
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AcceptRequestForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        request_id = kwargs.pop('request_id', None)
        super(AcceptRequestForm, self).__init__(*args, **kwargs)
        self.target_request = Request.objects.get(id=request_id)

        # load user provided fields and add admin field if exist
        if "spec" in self.target_request.operation.job_template.survey:
            self.fields = get_fields_from_survey(self.target_request.operation.job_template.survey,
                                                 self.target_request.operation.enabled_survey_fields)
            prefill_form_with_user_values(self.fields, self.target_request.fill_in_survey)

    def save(self):
        user_provided_survey_fields = dict()
        for field_key, value in self.cleaned_data.items():
            # tower doesnt allow empty value for choices fields
            if value != '':
                user_provided_survey_fields[field_key] = value
        # update the request
        self.target_request.fill_in_survey = user_provided_survey_fields
        self.target_request.accept()
        self.target_request.save()
        # reset the instance state if it was failed (in case of resetting the state)
        self.target_request.instance.reset_to_last_stable_state()
        self.target_request.instance.save()
