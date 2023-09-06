from profiles.models.squest_permission import Permission

from service_catalog.api.serializers.approval_step_serializer import ApprovalStepSerializer
from tests.test_service_catalog.base_test_approval import BaseTestApprovalAPI


class TestApprovalStepSerializer(BaseTestApprovalAPI):

    def setUp(self):
        super(TestApprovalStepSerializer, self).setUp()
        self.field1 = self.create_operation_test.tower_survey_fields.all()[0]
        self.field2 = self.create_operation_test.tower_survey_fields.all()[1]
        self.data = {
            'approval_workflow': self.test_approval_workflow.id,
            'name': 'test_step',
            'permission': Permission.objects.get(codename="approve_reject_approvalstep").id,
            'readable_fields': [self.field1.id],
            'editable_fields': [self.field2.id]
        }

    def test_valid_object(self):
        serializer = ApprovalStepSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

    def test_cannot_set_field_as_editable_and_readable_field(self):
        self.data['editable_fields'] = [self.field1.id]
        serializer = ApprovalStepSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("A Field Cannot Be Declared As Read And Write", serializer.errors["readable_fields"][0].title())
