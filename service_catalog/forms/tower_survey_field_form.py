from django import forms
from django.forms import SelectMultiple

from Squest.utils.plugin_controller import PluginController
from Squest.utils.squest_model_form import SquestModelForm
from service_catalog.models.tower_survey_field import TowerSurveyField


class TowerSurveyFieldForm(SquestModelForm):

    validators = forms.MultipleChoiceField(label="Validators",
                                           required=False,
                                           choices=[],
                                           widget=SelectMultiple(attrs={'data-live-search': "true"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        validator_choices = list()
        validator_files = [(file_name, file_name) for file_name in PluginController.get_user_provisioned_validators()]
        validator_choices.extend(validator_files)
        self.fields['validators'].choices = validator_choices
        if self.instance is not None and self.instance.validators is not None:
            # Converting comma separated string to python list
            instance_validator_as_list = self.instance.validators.split(",")
            # set the current value
            self.initial["validators"] = instance_validator_as_list

    def clean_validators(self):
        if not self.cleaned_data['validators']:
            return None
        return ",".join(self.cleaned_data['validators'])

    class Meta:
        model = TowerSurveyField
        fields = ["is_customer_field", "default", "validators", "attribute_definition"]
