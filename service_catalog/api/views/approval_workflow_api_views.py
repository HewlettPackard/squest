from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from Squest.utils.squest_api_views import SquestListCreateAPIView, SquestRetrieveUpdateDestroyAPIView, \
    SquestRetrieveAPIView
from service_catalog.api.serializers.approval_step_serializer import ApprovalStepPositionSerializer
from service_catalog.api.serializers.approval_workflow_serializer import ApprovalWorkflowSerializer
from service_catalog.api.serializers.approval_workflow_state_serializer import ApprovalWorkflowStateSerializer
from service_catalog.api.serializers.approve_workflow_step_serializer import ApproveWorkflowStepSerializer
from service_catalog.filters.approval_workflow_filter import ApprovalWorkflowFilter
from service_catalog.models import ApprovalWorkflow, ApprovalWorkflowState, Request, ApprovalStep


class ApprovalWorkflowListCreate(SquestListCreateAPIView):
    queryset = ApprovalWorkflow.objects.all()
    filterset_class = ApprovalWorkflowFilter
    serializer_class = ApprovalWorkflowSerializer


class ApprovalWorkflowDetails(SquestRetrieveUpdateDestroyAPIView):
    queryset = ApprovalWorkflow.objects.all()
    serializer_class = ApprovalWorkflowSerializer


class ApprovalWorkflowStateDetails(SquestRetrieveAPIView):
    serializer_class = ApprovalWorkflowStateSerializer
    queryset = ApprovalWorkflowState.objects.all()

    def get_serializer_context(self):
        return {"user": self.request.user}

    def get_object(self):
        return get_object_or_404(ApprovalWorkflowState, request__id=self.kwargs.get("pk"))


class ApproveCurrentStep(ViewSet):
    @swagger_auto_schema(responses={200: 'Approval survey'})
    @action(detail=True)
    def get_survey(self, request, pk=None):
        """
        Get the survey prefilled by user/admin.
        """
        target_request = get_object_or_404(Request, id=pk)
        if target_request.approval_workflow_state.current_step is None:
            return Response({"error": "No pending step to approve"}, status=HTTP_404_NOT_FOUND)
        if not request.user.has_perm(target_request.approval_workflow_state.current_step.approval_step.permission.get_permission_str,
                                     target_request):
            raise PermissionDenied

        serializer = ApproveWorkflowStepSerializer(target_request=target_request, user=request.user)
        return Response(serializer.data, status=HTTP_200_OK)

    @swagger_auto_schema(responses={200: 'Approve step'})
    @action(detail=True)
    def approve(self, request, pk=None):
        target_request = get_object_or_404(Request, id=pk)
        if target_request.approval_workflow_state.current_step is None:
            return Response({"error": "No pending step to approve"}, status=HTTP_404_NOT_FOUND)
        if not request.user.has_perm(target_request.approval_workflow_state.current_step.approval_step.permission.get_permission_str(),
                                     target_request):
            raise PermissionDenied
        serializer = ApproveWorkflowStepSerializer(data=request.data, target_request=target_request, user=request.user)
        if serializer.is_valid():
            serializer.save()
            # send_mail_request_update(target_request, user_applied_state=request.user)
            return Response({"success": "Step approved"}, status=HTTP_200_OK)
        return Response(serializer.error_messages, status=HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={200: 'Approve step'})
    @action(detail=True)
    def reject(self, request, pk=None):
        target_request = get_object_or_404(Request, id=pk)
        if target_request.approval_workflow_state.current_step is None:
            return Response({"error": "No pending step to approve"}, status=HTTP_404_NOT_FOUND)
        if not request.user.has_perm(target_request.approval_workflow_state.current_step.approval_step.permission.get_permission_str(),
                                     target_request):
            raise PermissionDenied
        # reject the current step if exist
        if target_request.approval_workflow_state is not None:
            target_request.approval_workflow_state.reject_current_step(request.user)
        # reject the request
        target_request.reject(request.user)
        target_request.save()
        # send_mail_request_update(target_request, user_applied_state=request.user, message=message)
        return Response({"success": "Step rejected"}, status=HTTP_200_OK)


class ApprovalWorkflowUpdateStepsPosition(APIView):

    def post(self, request, pk):
        approval_workflow = get_object_or_404(ApprovalWorkflow, pk=pk)
        instances = approval_workflow.approval_steps
        serializer = ApprovalStepPositionSerializer(instance=instances, data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        # check that given step id belong to the workflow
        list_approval_step = approval_workflow.approval_steps.all()
        for step_to_update in serializer.initial_data:
            if step_to_update["id"] not in [step.id for step in list_approval_step]:
                raise ValidationError(f"Invalid step ID for the approval workflow ID '{approval_workflow.id}'")
        # check that the given number of step correspond to the number of step present in the workflow
        if len(serializer.initial_data) != len(list_approval_step):
            raise ValidationError(f"Missing position. Given: {len(serializer.initial_data)}. "
                                  f"Required: {len(list_approval_step)}")
        # check that all position are given (from zero to number of step)
        for position_value in range(0, len(serializer.initial_data)):
            if not any(step["position"] == position_value for step in serializer.initial_data):
                raise ValidationError(f"Missing position {position_value}")
        # save the new given positions
        for step_to_update in serializer.initial_data:
            step = ApprovalStep.objects.get(id=step_to_update["id"])
            step.position = step_to_update["position"]
            step.save()
        return Response(serializer.data, status=HTTP_200_OK)
