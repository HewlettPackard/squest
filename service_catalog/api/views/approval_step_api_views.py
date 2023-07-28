from rest_framework.generics import get_object_or_404

from Squest.utils.squest_api_views import SquestListCreateAPIView, SquestRetrieveUpdateDestroyAPIView
from service_catalog.api.serializers.approval_step_serializer import ApprovalStepSerializer
from service_catalog.filters.approval_step_filter import ApprovalStepFilter
from service_catalog.models import ApprovalStep, ApprovalWorkflow


class ApprovalStepListCreate(SquestListCreateAPIView):
    serializer_class = ApprovalStepSerializer
    filterset_class = ApprovalStepFilter

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return ApprovalStep.objects.none()
        queryset = ApprovalStep.objects.filter(approval_workflow_id=self.kwargs['approval_workflow_id'])
        return queryset

    def get_serializer_context(self):
        context = super(ApprovalStepListCreate, self).get_serializer_context()
        approval_workflow = get_object_or_404(ApprovalWorkflow, pk=self.kwargs['approval_workflow_id'])
        context["approval_workflow_id"] = approval_workflow.id
        return context


class ApprovalStepDetails(SquestRetrieveUpdateDestroyAPIView):
    serializer_class = ApprovalStepSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return ApprovalStep.objects.none()
        queryset = ApprovalStep.objects.filter(approval_workflow_id=self.kwargs['approval_workflow_id'])
        return queryset

    def get_serializer_context(self):
        context = super(ApprovalStepDetails, self).get_serializer_context()
        approval_workflow = get_object_or_404(ApprovalWorkflow, pk=self.kwargs['approval_workflow_id'])
        context["approval_workflow_id"] = approval_workflow.id
        return context
