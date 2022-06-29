from django.core.exceptions import ValidationError

from service_catalog.models import Operation, ApprovalWorkflow, OperationType, Request, Instance
from service_catalog.models.approval_step import ApprovalStep
from service_catalog.models.approval_step_type import ApprovalStepType
from tests.test_service_catalog.base import BaseTest


class TestOperation(BaseTest):

    def setUp(self):
        super(TestOperation, self).setUp()

    def test_survey_from_job_template_is_copied_on_create(self):
        new_operation = Operation.objects.create(name="new test",
                                                 service=self.service_test,
                                                 job_template=self.job_template_test,
                                                 process_timeout_second=20)
        for field in self.job_template_test.survey["spec"]:
            self.assertTrue(new_operation.tower_survey_fields.filter(name=field["variable"], enabled=True).exists())

    def test_service_is_disabled_when_the_create_operation_disabled(self):
        self.assertTrue(self.create_operation_test.service.enabled)
        self.assertTrue(self.create_operation_test.enabled)
        self.create_operation_test.enabled = False
        self.create_operation_test.save()
        self.assertFalse(self.create_operation_test.service.enabled)
        self.assertFalse(self.create_operation_test.enabled)

    def test_can_create_operation_with_approval_workflow(self):
        approval_workflow = ApprovalWorkflow.objects.create(
            name="WF",
        )
        approval_step = ApprovalStep.objects.create(
            name="First",
            type=ApprovalStepType.AT_LEAST_ONE,
            approval_workflow=approval_workflow
        )
        approval_workflow.entry_point = approval_step
        approval_workflow.save()
        operation = Operation.objects.create(
            name="new test",
            service=self.service_test,
            type=OperationType.UPDATE,
            job_template=self.job_template_test,
            process_timeout_second=20,
            approval_workflow=approval_workflow
        )
        is_raise = False
        try:
            operation.clean()
        except ValidationError:
            is_raise = True
        self.assertEqual(is_raise, False)

    def test_cannot_create_operation_with_approval_workflow_and_auto_accept(self):
        approval_workflow = ApprovalWorkflow.objects.create(
            name="WF",
        )
        approval_step = ApprovalStep.objects.create(
            name="First",
            type=ApprovalStepType.AT_LEAST_ONE,
            approval_workflow=approval_workflow
        )
        approval_workflow.entry_point = approval_step
        approval_workflow.save()
        operation = Operation.objects.create(
            name="new test",
            service=self.service_test,
            type=OperationType.UPDATE,
            job_template=self.job_template_test,
            process_timeout_second=20,
            approval_workflow=approval_workflow,
            auto_accept=True
        )
        self.assertRaises(ValidationError, operation.clean)

    def test_cannot_create_operation_with_approval_workflow_without_entry_point(self):
        approval_workflow = ApprovalWorkflow.objects.create(
            name="WF",
        )
        approval_step = ApprovalStep.objects.create(
            name="First",
            type=ApprovalStepType.AT_LEAST_ONE,
            approval_workflow=approval_workflow
        )
        approval_workflow.entry_point = approval_step
        approval_workflow.save()
        operation = Operation.objects.create(
            name="new test",
            service=self.service_test,
            type=OperationType.UPDATE,
            job_template=self.job_template_test,
            process_timeout_second=20,
            approval_workflow=approval_workflow,
            auto_accept=True
        )
        self.assertRaises(ValidationError, operation.clean)

    def test_unset_approval_workflow_of_operation(self):
        approval_workflow = ApprovalWorkflow.objects.create(
            name="WF",
        )
        approval_step = ApprovalStep.objects.create(
            name="First",
            type=ApprovalStepType.AT_LEAST_ONE,
            approval_workflow=approval_workflow
        )
        approval_workflow.entry_point = approval_step
        approval_workflow.save()
        operation = Operation.objects.create(
            name="new test",
            service=self.service_test,
            type=OperationType.UPDATE,
            job_template=self.job_template_test,
            process_timeout_second=20,
            approval_workflow=approval_workflow,
            auto_accept=True
        )
        instance = Instance.objects.create(name="test")
        request = Request.objects.create(
            instance=instance,
            operation=operation,
            fill_in_survey={},
            user=self.standard_user
        )
        self.assertEqual(request.approval_step, approval_step)
        operation.approval_workflow = None
        operation.save()
        request.refresh_from_db()
        self.assertEqual(request.approval_step, None)
        operation.approval_workflow = approval_workflow
        operation.save()
        request.refresh_from_db()
        self.assertEqual(request.approval_step, approval_step)
