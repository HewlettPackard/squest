from profiles.models import Organization
from service_catalog.models import ApprovalWorkflow, ApprovalStepState, ApprovalStep, Instance, Request
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestApprovalWorkflow(BaseTestRequest):

    def setUp(self):
        super(TestApprovalWorkflow, self).setUp()

        self.test_approval_workflow_for_all_scopes = ApprovalWorkflow.objects.create(
            name="test_approval_workflow_for_all_scopes",
            operation=self.create_operation_test)

        self.test_approval_step_1 = ApprovalStep.objects.create(name="test_approval_step_1",
                                                                approval_workflow=self.test_approval_workflow_for_all_scopes)
        self.test_approval_step_2 = ApprovalStep.objects.create(name="test_approval_step_2",
                                                                approval_workflow=self.test_approval_workflow_for_all_scopes)

        self.test_approval_workflow_no_steps = ApprovalWorkflow.objects.create(name="test_approval_workflow_no_steps",
                                                                               operation=self.create_operation_test)

        self.org1 = Organization.objects.create(name="Org1")

        self.instance1 = Instance.objects.create(name="test_instance_1",
                                                 service=self.create_operation_test.service,
                                                 quota_scope=self.org1,
                                                 requester=self.standard_user)

    def test_first_step(self):
        self.assertEqual(self.test_approval_workflow_for_all_scopes.first_step, self.test_approval_step_1)
        self.assertIsNone(self.test_approval_workflow_no_steps.first_step)

    def test_instantiate(self):
        number_step_state_before = ApprovalStepState.objects.all().count()
        new_approval_workflow_state = self.test_approval_workflow_for_all_scopes.instantiate()
        self.assertEqual(number_step_state_before + 2, ApprovalStepState.objects.all().count())

        created_steps = ApprovalStepState.objects.filter(
            approval_workflow_state__approval_workflow=self.test_approval_workflow_for_all_scopes).order_by(
            'approval_step__position')
        first_step = created_steps.first()
        self.assertEqual(new_approval_workflow_state.current_step, first_step)

    def test_get_approval_workflow(self):
        # Create request with_quota_scope=org1 -> it will take the general workflow for self.create_operation_test
        self.request1 = Request.objects.create(instance=self.instance1, operation=self.create_operation_test)
        self.assertEqual(self.test_approval_workflow_for_all_scopes, self.request1._get_approval_workflow())

        # Create a workflow for org1
        self.test_approval_workflow_for_org1 = ApprovalWorkflow.objects.create(
            name="test_approval_workflow_for_org1",
            operation=self.create_operation_test)
        self.test_approval_workflow_for_org1.scopes.set([self.org1])

        # Create request with_quota_scope=org1 -> it will take the workflow dedicated to org1 for self.create_operation_test
        self.request2 = Request.objects.create(instance=self.instance1, operation=self.create_operation_test)
        self.assertEqual(self.test_approval_workflow_for_org1, self.request1._get_approval_workflow())
