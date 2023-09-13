from Squest.utils.squest_model_form import SquestModelForm
from service_catalog.models import InstanceHook, RequestHook


class InstanceHookForm(SquestModelForm):
    class Meta:
        model = InstanceHook
        fields = ["name", "services", "state", "job_template", "extra_vars"]


class RequestHookForm(SquestModelForm):
    class Meta:
        model = RequestHook
        fields = ["name", "operations", "state", "job_template", "extra_vars"]
