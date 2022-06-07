from Squest.utils.squest_model_form import SquestModelForm
from service_catalog.models import ApprovalWorkflow
from service_catalog.models.approval_step import ApprovalStep


class ApprovalStepForm(SquestModelForm):
    class Meta:
        model = ApprovalStep
        fields = ["name", "type", "teams"]

    def __init__(self, *args, **kwargs):
        self.approval_workflow_id = kwargs.pop('approval_workflow_id')
        super(ApprovalStepForm, self).__init__(*args, **kwargs)
        self.instance.approval_workflow = ApprovalWorkflow.objects.get(id=self.approval_workflow_id)
