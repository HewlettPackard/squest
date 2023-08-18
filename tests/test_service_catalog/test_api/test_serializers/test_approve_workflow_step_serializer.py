from unittest import mock

from service_catalog.api.serializers.approve_workflow_step_serializer import ApproveWorkflowStepSerializer
from tests.test_service_catalog.base_test_approval import BaseTestApprovalAPI


class TestApproveWorkflowStepSerializer(BaseTestApprovalAPI):

    def setUp(self):
        super(TestApproveWorkflowStepSerializer, self).setUp()

    def test_approve_workflow_step(self):
        parameters = {
            'target_request': self.test_request,
            'user': self.superuser
        }
        data = {
            'text_variable': 'string',
            'multiplechoice_variable': "choice1"
        }
        serializer = ApproveWorkflowStepSerializer(data=data, **parameters)
        self.assertTrue(serializer.is_valid())
        with mock.patch("service_catalog.models.approval_workflow_state.ApprovalWorkflowState.approve_current_step") as mock_approve_current_step:
            serializer.save()
            # only the editable field is sent to approve
            mock_approve_current_step.assert_called_with(user=self.superuser,
                                                         fill_in_survey={'multiplechoice_variable': 'choice1'})
