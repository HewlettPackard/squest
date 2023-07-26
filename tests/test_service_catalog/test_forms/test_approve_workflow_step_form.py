from unittest import mock

from service_catalog.forms.approve_workflow_step_form import ApproveWorkflowStepForm
from service_catalog.models import ApprovalWorkflow, ApprovalStep
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestApproveWorkflowStepForm(BaseTestRequest):

    def setUp(self):
        super(TestApproveWorkflowStepForm, self).setUp()
        self.create_operation_test.update_survey()
        self.test_approval_workflow = ApprovalWorkflow.objects.create(name="test_approval_workflow",
                                                                      operation=self.create_operation_test)

        self.test_approval_step_1 = ApprovalStep.objects.create(name="test_approval_step_1",
                                                                approval_workflow=self.test_approval_workflow)
        self.test_approval_workflow_state = self.test_approval_workflow.instantiate()
        self.test_request.approval_workflow_state = self.test_approval_workflow_state
        self.test_request.save()
        self.test_approval_step_1.readable_fields.set([self.create_operation_test.tower_survey_fields.all()[0]])
        self.test_approval_step_1.editable_fields.set([self.create_operation_test.tower_survey_fields.all()[1]])

    def test_approve_workflow_step(self):
        parameters = {
            'target_request': self.test_request,
            'user': self.superuser
        }
        data = {
            'text_variable': 'string',
            'multiplechoice_variable': "choice1"
        }
        form = ApproveWorkflowStepForm(data, **parameters)
        self.assertTrue(form.is_valid())
        with mock.patch("service_catalog.models.approval_workflow_state.ApprovalWorkflowState.approve_current_step") as mock_approve_current_step:
            form.save()
            # only the editable field is sent to approve
            mock_approve_current_step.assert_called_with(user=self.superuser,
                                                         fill_in_survey={'multiplechoice_variable': 'choice1'})
