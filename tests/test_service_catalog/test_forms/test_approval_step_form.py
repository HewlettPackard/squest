from profiles.models.squest_permission import Permission

from service_catalog.forms.approval_step_form import ApprovalStepForm
from service_catalog.models import ApprovalWorkflow
from tests.test_service_catalog.base import BaseTest


class TestApprovalStepForm(BaseTest):

    def setUp(self):
        super(TestApprovalStepForm, self).setUp()
        self.test_approval_workflow = ApprovalWorkflow.objects.create(name="test_approval_workflow",
                                                                      operation=self.create_operation_test)
        self.create_operation_test.update_survey()
        self.field1 = self.create_operation_test.tower_survey_fields.all()[0]
        self.field2 = self.create_operation_test.tower_survey_fields.all()[1]

    def test_create_approval_step(self):
        parameters = {
            'approval_workflow': self.test_approval_workflow
        }
        data = {
            'approval_workflow': self.test_approval_workflow.id,
            'name': 'test_step',
            'permission': Permission.objects.get(codename="can_approve_approvalstep"),
            'readable_fields': [self.field1],
            'editable_fields': [self.field2]
        }
        form = ApprovalStepForm(data, **parameters)
        self.assertTrue(form.is_valid())

    def test_cannot_set_field_as_editable_and_readable_field(self):
        parameters = {
            'approval_workflow': self.test_approval_workflow
        }
        data = {
            'name': 'test_step',
            'permission': Permission.objects.get(codename="can_approve_approvalstep"),
            'readable_fields': [self.field1],
            'editable_fields': [self.field1]
        }
        form = ApprovalStepForm(data, **parameters)
        self.assertFalse(form.is_valid())
        self.assertIn("A field cannot be declared as read and write", form["readable_fields"].errors[0])
