from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser

from service_catalog.api.serializers.approval_workflow_serializer import ApprovalWorkflowSerializer
from service_catalog.filters.approval_workflow_filter import ApprovalWorkflowFilter
from service_catalog.models.approval_workflow import ApprovalWorkflow


class ApprovalWorkflowDetails(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = ApprovalWorkflow.objects.all()
    serializer_class = ApprovalWorkflowSerializer


class ApprovalWorkflowListCreate(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = ApprovalWorkflow.objects.all()
    filterset_class = ApprovalWorkflowFilter
    serializer_class = ApprovalWorkflowSerializer
