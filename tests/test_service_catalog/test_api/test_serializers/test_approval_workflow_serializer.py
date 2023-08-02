from profiles.models import GlobalPermission
from service_catalog.api.serializers.approval_step_state_serializer import ApprovalStepStateSerializer
from service_catalog.api.serializers.approval_workflow_serializer import ApprovalWorkflowSerializer
from tests.test_service_catalog.base_test_approval import BaseTestApprovalAPI


class TestApprovalWorkflowSerializer(BaseTestApprovalAPI):

    def setUp(self):
        super(TestApprovalWorkflowSerializer, self).setUp()
        self.test_approval_workflow.scopes.set([self.test_quota_scope])
        self.test_approval_workflow.save()

    def test_cannot_valid_when_scope_already_present_in_another_workflow(self):
        data = {
            "name": "test_workflow",
            "operation": self.create_operation_test.id,
            "scopes": [self.test_quota_scope.id]
        }
        serializer = ApprovalWorkflowSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Has Already An Approval Workflow Based On This Operation", serializer.errors["scopes"][0].title())
