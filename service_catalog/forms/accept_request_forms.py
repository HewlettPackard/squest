import urllib3
from django import forms

from profiles.models import BillingGroup
from service_catalog.forms.utils import get_fields_from_survey, prefill_form_with_user_values
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AcceptRequestForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.target_request = kwargs.pop('request', None)
        super(AcceptRequestForm, self).__init__(*args, **kwargs)
        self.fields["instance_name"] = forms.CharField(label="Name", initial=self.target_request.instance.name, widget=forms.TextInput(attrs={"class": "form-control"}))
        self.fields["billing_group_id"] = forms.ModelChoiceField(
            label="Billing group",
            initial=self.target_request.instance.billing_group,
            queryset=BillingGroup.objects.all(),
            required=False,
            widget=forms.Select(attrs={"class": "form-control selectpicker", "data-live-search": "true"})
        )
        self.fields["instance_name"].group = "1. Instance"
        self.fields["billing_group_id"].group = "1. Instance"
        # load user provided fields and add admin field if exist
        if "spec" in self.target_request.operation.job_template.survey:
            self.fields.update(get_fields_from_survey(self.target_request.operation.job_template.survey,
                                                      self.target_request.operation.enabled_survey_fields))
            prefill_form_with_user_values(self.fields, self.target_request.fill_in_survey)

    def save(self):
        user_provided_survey_fields = dict()
        for field_key, value in self.cleaned_data.items():
            # tower doesnt allow empty value for choices fields
            if value != '' and field_key not in ['instance_name', 'billing_group_id']:
                user_provided_survey_fields[field_key] = value
        # update the request
        self.target_request.fill_in_survey = user_provided_survey_fields
        self.target_request.accept()
        self.target_request.save()
        # reset the instance state if it was failed (in case of resetting the state)
        self.target_request.instance.reset_to_last_stable_state()
        self.target_request.instance.billing_group = self.cleaned_data["billing_group_id"]
        self.target_request.instance.name = self.cleaned_data["instance_name"]
        self.target_request.instance.save()
