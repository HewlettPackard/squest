from Squest.utils.squest_filter import SquestFilter
from service_catalog.models import ApprovalStep


class ApprovalStepFilter(SquestFilter):
    class Meta:
        model = ApprovalStep
        fields = ["name"]
