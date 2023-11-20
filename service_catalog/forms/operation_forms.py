from Squest.utils.squest_model_form import SquestModelForm
from service_catalog.models import Operation


class OperationForm(SquestModelForm):
    class Meta:
        model = Operation
        fields = ["service", "name", "description", "job_template", "type", "process_timeout_second",
                  "auto_accept", "auto_process", "enabled", "is_admin_operation", "extra_vars", "default_inventory_id",
                  "default_limits", "default_tags", "default_skip_tags", "default_credentials_ids", "default_verbosity",
                  "default_diff_mode", "default_job_type"]
