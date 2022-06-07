from operator import xor

from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404, CreateAPIView
from rest_framework.permissions import IsAdminUser

from service_catalog.api.serializers.approval_step_serializer import ApprovalStepSerializer
from service_catalog.filters.approval_step_filter import ApprovalStepFilter
from service_catalog.models import ApprovalWorkflow
from service_catalog.models.approval_step import ApprovalStep


class ApprovalStepDetails(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = ApprovalStep.objects.all()
    serializer_class = ApprovalStepSerializer


class ApprovalStepListCreate(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    filterset_class = ApprovalStepFilter
    serializer_class = ApprovalStepSerializer

    def get_queryset(self):
        return ApprovalStep.objects.filter(approval_workflow_id=self.kwargs.get("approval_workflow_id"))

    def perform_create(self, serializer):
        approval_workflow = get_object_or_404(ApprovalWorkflow, id=self.kwargs.get("approval_workflow_id"))
        previous_id = serializer.validated_data.pop('previous_id', None)
        previous = get_object_or_404(ApprovalStep.objects.filter(approval_workflow=approval_workflow),
                                     id=previous_id) if previous_id else None
        if xor(bool(approval_workflow.entry_point), bool(previous_id)):
            if approval_workflow.entry_point:
                raise PermissionDenied(detail="An entry point already exist in this approval workflow please use the *"
                                              "create next url to add the following steps of the workflow.")
            else:
                raise PermissionDenied(detail="You must create an entry point in this workflow.")
        approval_step = serializer.save(approval_workflow=approval_workflow)
        next_approval_step_id = None
        if previous:
            next_approval_step_id = previous.next.id if previous.next else None
            previous.set_next(approval_step.id)
        approval_step.set_next(next_approval_step_id)