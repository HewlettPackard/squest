from profiles.models import Permission
from service_catalog.models import ApprovalWorkflow, ApprovalStep, Instance, Request, ApprovalWorkflowState
from tests.setup import SetupOperation, SetupOrg
from tests.utils import TransactionTestUtils


class TestApprovalWorkflowVersion(TransactionTestUtils, SetupOperation, SetupOrg):

    def setUp(self):
        SetupOperation.setUp(self)
        SetupOrg.setUp(self)

    def test_hash(self):
        # Create ApprovalWorkflow
        aw = ApprovalWorkflow.objects.create(
            name="AW - All scopes",
            operation=self.operation_create_1,
            enabled=True
        )
        old_hash = aw.hash
        #############################################
        # Test hash when adding new step
        #############################################
        as1 = ApprovalStep.objects.create(name="step 1", approval_workflow=aw)

        self.assertNotEqual(aw.hash, old_hash)
        old_hash = aw.hash

        #############################################
        # Test hash when editing step name
        #############################################
        as1.name = "Step 1"
        self.assertEqual(aw.hash, old_hash)
        as1.save()
        self.assertEqual(aw.hash, old_hash)
        old_hash = aw.hash

        #############################################
        # Test hash when creating second step
        #############################################
        as2 = ApprovalStep.objects.create(name="Step 2", approval_workflow=aw)
        self.assertNotEqual(aw.hash, old_hash)
        old_hash = aw.hash

        #############################################
        # Test hash when editing step permission
        #############################################
        as2.permission = Permission.objects.first()
        as2.save()
        self.assertNotEqual(aw.hash, old_hash)
        old_hash = aw.hash

        #############################################
        # Test hash when editing readable fields
        #############################################
        tower_survey_field = as2.approval_workflow.operation.tower_survey_fields.first()
        self.assertIsNotNone(tower_survey_field)
        as2.readable_fields.add(tower_survey_field)
        self.assertNotEqual(aw.hash, old_hash)
        old_hash = aw.hash

        #############################################
        # Test hash when editing editable fields
        #############################################
        tower_survey_field = as1.approval_workflow.operation.tower_survey_fields.last()
        self.assertIsNotNone(tower_survey_field)
        as1.editable_fields.add(tower_survey_field)
        self.assertNotEqual(aw.hash, old_hash)
        old_hash = aw.hash

        #############################################
        # Test hash when deleting step
        #############################################
        as2.delete()
        self.assertNotEqual(aw.hash, old_hash)
        old_hash = aw.hash

        #############################################
        # Test hash when AW is disable
        #############################################
        aw.enabled = False
        aw.save()
        self.assertNotEqual(aw.hash, old_hash)

    def test_approval_workflow_state_take_hash(self):
        aw = ApprovalWorkflow.objects.create(
            name="AW - All scopes",
            operation=self.operation_create_1,
            enabled=True
        )
        aw_hash = aw.hash
        self.instance_1 = Instance.objects.create(name="Instance 1", quota_scope=self.org1, service=self.service_1)
        self.request_1 = Request.objects.create(instance=self.instance_1, operation=self.operation_create_1)

        # AW version is the same even after instantiate()
        self.assertEqual(aw.hash, aw_hash)
        self.assertEqual(self.request_1.approval_workflow_state.hash, aw_hash)

        # Ensure that resetting doesn't increment version
        ApprovalStep.objects.create(name="step 1", approval_workflow=aw)
        # Hash changed
        self.assertNotEqual(aw.hash, aw_hash)
        # ApprovalWorkflowState still use the old hash
        self.assertEqual(self.request_1.approval_workflow_state.hash, aw_hash)
