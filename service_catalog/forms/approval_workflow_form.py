from Squest.utils.squest_model_form import SquestModelForm
from service_catalog.models.approval_workflow import ApprovalWorkflow


class ApprovalWorkflowForm(SquestModelForm):
    class Meta:
        model = ApprovalWorkflow
        fields = ["name"]
