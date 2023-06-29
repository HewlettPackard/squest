import urllib3
from django import forms

from profiles.models.scope import Scope
from service_catalog.forms.form_utils import FormUtils
from service_catalog.forms.utils import get_fields_from_survey, prefill_form_with_user_values

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AcceptRequestForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.target_request = kwargs.pop('request', None)
        super(AcceptRequestForm, self).__init__(*args, **kwargs)
        self.fields["squest_instance_name"] = forms.CharField(label="Name",
                                                              initial=self.target_request.instance.name,
                                                              widget=forms.TextInput(attrs={"class": "form-control"}))
        self.fields["quota_scope_id"] = forms.ModelChoiceField(
            label="Quota",
            initial=self.target_request.instance.quota_scope,
            queryset=Scope.objects.all(),
            required=False,
            widget=forms.Select(attrs={"class": "form-control selectpicker", "data-live-search": "true"})
        )
        instance_group_name = f"1. Instance"
        self.fields["squest_instance_name"].group = instance_group_name
        self.fields["quota_scope_id"].group = instance_group_name
        # load user provided fields and add admin field if exist
        if "spec" in self.target_request.operation.job_template.survey:
            from service_catalog.api.serializers import RequestSerializer
            context = {
                "request": RequestSerializer(self.target_request).data
            }
            purged_survey_with_default = FormUtils.apply_jinja_template_to_survey(job_template_survey=self.target_request.operation.job_template.survey,
                                                                                  operation_survey=self.target_request.operation.tower_survey_fields,
                                                                                  context=context
                                                                                  )
            purged_survey_with_validator = FormUtils.apply_user_validator_to_survey(
                job_template_survey=purged_survey_with_default,
                operation_survey=self.target_request.operation.tower_survey_fields)
            self.fields.update(get_fields_from_survey(purged_survey_with_validator,
                                                      self.target_request.operation.tower_survey_fields))
            prefill_form_with_user_values(self.fields, self.target_request.fill_in_survey,
                                          self.target_request.admin_fill_in_survey)

    def save(self):
        user_provided_survey_fields = dict()
        for field_key, value in self.cleaned_data.items():
            if field_key not in ['squest_instance_name', 'quota_scope_id']:
                user_provided_survey_fields[field_key] = value
        # update the request
        self.target_request.update_fill_in_surveys_accept_request(user_provided_survey_fields)
        self.target_request.save()
        # reset the instance state if it was failed (in case of resetting the state)
        self.target_request.instance.reset_to_last_stable_state()
        self.target_request.instance.scope = self.cleaned_data["quota_scope_id"]
        self.target_request.instance.name = self.cleaned_data["squest_instance_name"]
        self.target_request.instance.save()
        return self.target_request
