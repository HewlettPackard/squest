from service_catalog.api.serializers.approval_workflow_serializer import ApprovalWorkflowSerializer, \
    ApprovalWorkflowSerializerEdit
from service_catalog.models import ApprovalWorkflow
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
        self.assertIn("has already an approval workflow based on this operation", serializer.errors["scopes"][0])

    def test_can_add_another_scope_to_scopes(self):
        data = {
            "name": "test_workflow",
            "operation": self.create_operation_test.id,
            "scopes": [self.test_quota_scope.id, self.test_quota_scope2.id]
        }
        serializer = ApprovalWorkflowSerializerEdit(instance=self.test_approval_workflow, data=data)
        self.assertTrue(serializer.is_valid())

    def test_cannot_valid_with_empty_scopes_if_already_exists(self):
        existing_approval = ApprovalWorkflow.objects.create(name="test",
                                                            operation=self.create_operation_test,
                                                            enabled=True)
        data = {
            "name": "test_workflow",
            "operation": self.create_operation_test.id,
        }
        serializer = ApprovalWorkflowSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("An approval workflow for all scopes already exists", serializer.errors["scopes"][0])

    def test_cannot_change_operation_when_edit(self):
        existing_approval = ApprovalWorkflow.objects.create(name="test",
                                                            operation=self.create_operation_test_2,
                                                            enabled=True)
        data = {
            "name": "test_workflow",
            "operation": self.create_operation_test.id,
        }
        serializer = ApprovalWorkflowSerializerEdit(instance=existing_approval, data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(existing_approval.operation, self.create_operation_test_2)
