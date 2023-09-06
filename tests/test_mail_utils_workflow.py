from django.contrib.auth.models import User

from profiles.models import Role, Permission
from service_catalog.mail_utils import _get_receivers_for_request

from service_catalog.models import Instance, Request, ApprovalWorkflow, ApprovalStep
from tests.test_service_catalog.base import BaseTest


class TestMailUtilsWorkflow(BaseTest):

    def setUp(self):
        super(TestMailUtilsWorkflow, self).setUp()

        # Create approval workflow
        self.approval_worklflow = ApprovalWorkflow.objects.create(operation=self.create_operation_test)
        self.approval_worklflow.scopes.set([self.test_quota_scope])
        self.approval_worklflow.save()

        self.approval_step1 = ApprovalStep(name="Step 1", approval_workflow=self.approval_worklflow)
        self.approval_step1.permission = Permission.objects.get_by_natural_key(codename="approve_reject_approvalstep",
                                                                               app_label="service_catalog",
                                                                               model="approvalstep")
        self.approval_step1.save()

        self.test_instance = Instance.objects.create(name="test_instance_1",
                                                     service=self.service_test,
                                                     spec={
                                                         "value1": "key1"
                                                     },
                                                     requester=self.standard_user,
                                                     quota_scope=self.test_quota_scope)
        self.test_request = Request.objects.create(
            fill_in_survey={
                'text_variable': 'my_var',
                'multiplechoice_variable': 'choice1', 'multiselect_var': 'multiselect_1',
                'textarea_var': '2',
                'password_var': 'pass',
                'integer_var': '1',
                'float_var': '0.6'
            },
            instance=self.test_instance,
            operation=self.create_operation_test,
            user=self.standard_user
        )

    def test_get_admin_emails_with_request(self):
        approver = User.objects.create(username='approver', email="approver@local.com")
        role_approver = Role.objects.create(name="Approver")
        role_approver.permissions.add(self.approval_step1.permission)

        self.test_quota_scope.add_user_in_role(approver, role_approver)
        self.assertCountEqual([self.superuser.email, self.superuser_2.email, approver.email],
                              _get_receivers_for_request(self.test_request))
