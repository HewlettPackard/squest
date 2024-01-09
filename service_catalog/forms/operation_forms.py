from django.forms import MultipleChoiceField, SelectMultiple

from Squest.utils.plugin_controller import PluginController
from Squest.utils.squest_model_form import SquestModelForm
from service_catalog.models import Operation


class OperationForm(SquestModelForm):
    validators = MultipleChoiceField(label="Validators",
                                     required=False,
                                     choices=[],
                                     widget=SelectMultiple(attrs={'data-live-search': "true"}))

    class Meta:
        model = Operation
        fields = ["service", "name", "description", "job_template", "type", "process_timeout_second",
                  "auto_accept", "auto_process", "enabled", "is_admin_operation", "extra_vars", "default_inventory_id",
                  "default_limits", "default_tags", "default_skip_tags", "default_credentials_ids", "default_verbosity",
                  "default_diff_mode", "default_job_type", "validators"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        validator_choices = list()
        validator_files = [(file_name, file_name) for file_name in
                           PluginController.get_user_provisioned_survey_validators()]
        validator_choices.extend(validator_files)
        self.fields['validators'].choices = validator_choices
        if self.instance is not None:
            if self.instance.validators is not None:
                # Converting comma separated string to python list
                instance_validator_as_list = self.instance.validators.split(",")
                # set the current value
                self.initial["validators"] = instance_validator_as_list

    def clean_validators(self):
        if not self.cleaned_data['validators']:
            return None
        return ",".join(self.cleaned_data['validators'])
