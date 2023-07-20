from Squest.utils.squest_model_form import SquestModelForm
from service_catalog.models import Request


class RequestForm(SquestModelForm):
    class Meta:
        model = Request
        exclude = ["periodic_task", "periodic_task_date_expire", "approval_workflow_state"]
