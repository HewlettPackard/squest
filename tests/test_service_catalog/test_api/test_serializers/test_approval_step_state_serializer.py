from profiles.models import GlobalPermission
from service_catalog.api.serializers.approval_step_state_serializer import ApprovalStepStateSerializer
from tests.test_service_catalog.base_test_approval import BaseTestApprovalAPI


class TestApprovalStepSerializer(BaseTestApprovalAPI):

    def setUp(self):
        super(TestApprovalStepSerializer, self).setUp()
        self.test_request.approval_workflow_state.current_step.fill_in_survey = {"test_key": "test_value"}
        self.test_request.approval_workflow_state.current_step.save()
        self.global_perm = GlobalPermission.load()

    def test_representation(self):
        serializer = ApprovalStepStateSerializer(user=self.standard_user)
        representation = serializer.to_representation(self.test_request.approval_workflow_state.current_step)
        self.assertTrue("fill_in_survey" not in representation)

        # give the perm to the user
        self.global_perm.default_permissions.add(self.test_request.approval_workflow_state.current_step.approval_step.permission)
        representation = serializer.to_representation(self.test_request.approval_workflow_state.current_step)
        self.assertTrue("fill_in_survey" in representation)
