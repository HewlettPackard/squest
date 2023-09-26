from Squest.utils.squest_api_views import SquestListCreateAPIView, SquestRetrieveUpdateDestroyAPIView
from service_catalog.api.serializers.approval_step_serializer import ApprovalStepSerializer
from service_catalog.filters.approval_step_filter import ApprovalStepFilter
from service_catalog.models import ApprovalStep


class ApprovalStepListCreate(SquestListCreateAPIView):
    serializer_class = ApprovalStepSerializer
    filterset_class = ApprovalStepFilter
    queryset = ApprovalStep.objects.all()


class ApprovalStepDetails(SquestRetrieveUpdateDestroyAPIView):
    serializer_class = ApprovalStepSerializer
    queryset = ApprovalStep.objects.all()
