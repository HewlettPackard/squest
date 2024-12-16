from django.forms import MultipleChoiceField, SelectMultiple, CharField, ModelChoiceField, forms

from Squest.utils.plugin_controller import PluginController
from Squest.utils.squest_model_form import SquestModelForm
from profiles.models import Permission
from service_catalog.forms.form_utils import FormUtils

from service_catalog.models import Operation

class OperationForm(SquestModelForm):
    validators = MultipleChoiceField(label="Validators",
                                     required=False,
                                     choices=[],
                                     widget=SelectMultiple(attrs={'data-live-search': "true"}))

    permission = ModelChoiceField(queryset=Permission.objects.filter(content_type__model="operation",
                                                                     content_type__app_label="service_catalog"),
                                  initial=FormUtils.get_default_permission_for_operation,
                                  help_text=Operation.permission.field.help_text)

    class Meta:
        model = Operation
        fields = ["service", "name", "description", "job_template", "type", "process_timeout_second",
                  "auto_accept", "auto_process", "enabled", "extra_vars", "default_inventory_id",
                  "default_limits", "default_tags", "default_skip_tags", "default_credentials_ids", "default_verbosity",
                  "default_diff_mode", "default_job_type", "validators", "when", "permission"]

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
                instance_validator_as_list = self.instance.validators_name
                # set the current value
                self.initial["validators"] = instance_validator_as_list

    def clean_validators(self):
        if not self.cleaned_data['validators']:
            return None
        return ",".join(self.cleaned_data['validators'])
