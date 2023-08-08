from django.test import TestCase
from rest_framework.test import APITestCase

from service_catalog.models import ApprovalWorkflow, ApprovalStep
from tests.test_service_catalog.base_test_request import BaseTestRequestCommon


class BaseTestApprovalCommon(BaseTestRequestCommon):

    def setUp(self):
        super(BaseTestApprovalCommon, self).setUp()

        # approval
        self.test_approval_workflow = ApprovalWorkflow.objects.create(name="test_approval_workflow",
                                                                      operation=self.create_operation_test)

        self.test_approval_step_1 = ApprovalStep.objects.create(name="test_approval_step_1",
                                                                approval_workflow=self.test_approval_workflow)
        self.test_approval_step_2 = ApprovalStep.objects.create(name="test_approval_step_2",
                                                                approval_workflow=self.test_approval_workflow)
        self.test_approval_workflow_state = self.test_approval_workflow.instantiate()
        self.test_request.approval_workflow_state = self.test_approval_workflow_state
        self.test_request.save()
        self.test_approval_step_1.readable_fields.set([self.create_operation_test.survey_fields.all()[0]])
        self.test_approval_step_1.editable_fields.set([self.create_operation_test.survey_fields.all()[1]])


class BaseTestApproval(TestCase, BaseTestApprovalCommon):
    pass


class BaseTestApprovalAPI(APITestCase, BaseTestApprovalCommon):
    pass
