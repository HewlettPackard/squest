from django import forms

from service_catalog.forms import FormGenerator


class AcceptRequestForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.target_request = kwargs.pop('request', None)
        super(AcceptRequestForm, self).__init__(*args, **kwargs)
        form_generator = FormGenerator(squest_request=self.target_request)
        self.fields.update(form_generator.generate_form())

    def save(self):
        user_provided_survey_fields = dict()
        for field_key, value in self.cleaned_data.items():
            user_provided_survey_fields[field_key] = value
        # update the request
        self.target_request.admin_fill_in_survey = user_provided_survey_fields
        self.target_request.save()
        # reset the instance state if it was failed (in case of resetting the state)
        self.target_request.instance.reset_to_last_stable_state()
        self.target_request.instance.save()
        return self.target_request
