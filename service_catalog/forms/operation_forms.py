from service_catalog.models import Operation
from Squest.utils.squest_model_form import SquestModelForm


class ServiceOperationForm(SquestModelForm):
    def __init__(self, *args, **kwargs):
        self.service = kwargs.pop("service")
        super(ServiceOperationForm, self).__init__(*args, **kwargs)
        choice_type = [('CREATE', 'Create'), ('UPDATE', 'Update'), ('DELETE', 'Delete')]
        # Default behavior
        self.fields['type'].choices = choice_type
        self.fields['type'].initial = self.fields['type'].choices[0]

    def save(self, commit=True):
        new_operation = super(ServiceOperationForm, self).save(commit=False)
        new_operation.service = self.service
        new_operation.save()
        return new_operation


    class Meta:
        model = Operation
        fields = ["name", "description", "job_template", "type", "process_timeout_second",
                  "auto_accept", "auto_process", "enabled", "is_admin_operation", "extra_vars", "default_inventory_id",
                  "default_limits", "default_tags", "default_skip_tags", "default_credentials_ids", "default_verbosity",
                  "default_diff_mode", "default_job_type"]
