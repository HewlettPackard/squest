from Squest.utils.squest_filter import SquestFilter
from service_catalog.models.approval_workflow import ApprovalWorkflow


class ApprovalWorkflowFilter(SquestFilter):
    class Meta:
        model = ApprovalWorkflow
        fields = ["name", "enabled"]
