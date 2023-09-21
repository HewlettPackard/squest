
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from profiles.models import Permission, Role, Organization
from service_catalog.models import Instance, InstanceState, Request, RequestState, ApprovalWorkflow, ApprovalStep
from tests.test_service_catalog.base import BaseTestCommon

class TestRequestsAwaitingApproval(BaseTestCommon):

    def setUp(self):
        super(TestRequestsAwaitingApproval, self).setUp()
        # Organization 1 - quota scope - role on org
        self.organization1 = Organization.objects.create(name="Organization 1")
        self.instance1 = Instance.objects.create(
            name="Instance 1",
            quota_scope=self.organization1,
            state=InstanceState.PENDING,
            service=self.service_test)
        self.user1 = User.objects.create_user(username="user1", email="user1@squest.local")

        self.organization2 = Organization.objects.create(name="Organization 2")
        self.instance2 = Instance.objects.create(
            name="Instance 2",
            quota_scope=self.organization2,
            state=InstanceState.PENDING,
            service=self.service_test)
        self.user2 = User.objects.create_user(username="user2", email="user2@squest.local")

    def test_approvalworkflow_request(self):
        # Prepare workflow1 for user 1 and wokflow2 for user 2

        # Approval workflow1
        approval_workflow1 = ApprovalWorkflow.objects.create(name="approval_workflow1",
                                                             operation=self.create_operation_test)
        approval_workflow1.scopes.set([self.organization1])
        content_type = ContentType.objects.get_for_model(ApprovalStep)
        permission_step1 = Permission.objects.create(codename="approve_step1", content_type=content_type)

        ApprovalStep.objects.create(name='approval_step1',
                                    approval_workflow=approval_workflow1,
                                    permission=permission_step1)

        role_approve_step1 = Role.objects.create(name="role_approve_step1")
        role_approve_step1.permissions.add(permission_step1)
        self.organization1.add_user_in_role(self.user1, role_approve_step1)

        # Approval workflow2
        approval_workflow2 = ApprovalWorkflow.objects.create(name="approval_workflow2",
                                                             operation=self.create_operation_test)
        approval_workflow2.scopes.set([self.organization2])
        content_type = ContentType.objects.get_for_model(ApprovalStep)
        permission_step2 = Permission.objects.create(codename="approve_step2", content_type=content_type)

        ApprovalStep.objects.create(name='approval_step2',
                                    approval_workflow=approval_workflow2,
                                    permission=permission_step2)

        role_approve_step2 = Role.objects.create(name="role_approve_step2")
        role_approve_step2.permissions.add(permission_step2)
        self.organization2.add_user_in_role(self.user2, role_approve_step2)

        # Start test
        ## No requests -> empty for all
        self.assertCountEqual(Request.get_requests_awaiting_approval(self.user1).values_list('id', flat=True), [])
        self.assertCountEqual(Request.get_requests_awaiting_approval(self.user2).values_list('id', flat=True), [])
        self.assertCountEqual(Request.get_requests_awaiting_approval(self.superuser).values_list('id', flat=True), [])

        ## Create request for instance1 that will trigger workflow1
        self.request_approvalwf_1 = Request.objects.create(instance=self.instance1,
                                                           state=RequestState.SUBMITTED,
                                                           operation=self.create_operation_test)

        ## user1 and admin can see it
        self.assertCountEqual(Request.get_requests_awaiting_approval(self.user1).values_list('id', flat=True),
                              [self.request_approvalwf_1.id])
        self.assertCountEqual(Request.get_requests_awaiting_approval(self.user2).values_list('id', flat=True), [])
        self.assertCountEqual(Request.get_requests_awaiting_approval(self.superuser).values_list('id', flat=True),
                              [self.request_approvalwf_1.id])

        ## Create request for instance2 that will trigger workflow2
        self.request_approvalwf_2 = Request.objects.create(instance=self.instance2,
                                                           state=RequestState.SUBMITTED,
                                                           operation=self.create_operation_test)
        ## user1 doesn't see the new one. user2 and admin can see it
        self.assertCountEqual(Request.get_requests_awaiting_approval(self.user1).values_list('id', flat=True),
                              [self.request_approvalwf_1.id])
        self.assertCountEqual(Request.get_requests_awaiting_approval(self.user2).values_list('id', flat=True),
                              [self.request_approvalwf_2.id])
        self.assertCountEqual(Request.get_requests_awaiting_approval(self.superuser).values_list('id', flat=True),
                              [self.request_approvalwf_1.id, self.request_approvalwf_2.id])

    def test_classic_request(self):

        approver = Role.objects.create(name="approver")
        approver.permissions.add(Permission.objects.get_by_natural_key(codename="accept_request",app_label="service_catalog",model="request"))
        self.organization1.add_user_in_role(self.user1, approver)
        self.organization2.add_user_in_role(self.user2, approver)

        self.assertCountEqual(Request.get_requests_awaiting_approval(self.user1).values_list('id', flat=True), [])
        self.assertCountEqual(Request.get_requests_awaiting_approval(self.user2).values_list('id', flat=True), [])
        self.assertCountEqual(Request.get_requests_awaiting_approval(self.superuser).values_list('id', flat=True), [])

        self.request_approvalwf_1 = Request.objects.create(instance=self.instance1,
                                                           state=RequestState.SUBMITTED,
                                                           operation=self.create_operation_test)

        self.assertCountEqual(Request.get_requests_awaiting_approval(self.user1).values_list('id', flat=True),
                              [self.request_approvalwf_1.id])
        self.assertCountEqual(Request.get_requests_awaiting_approval(self.user2).values_list('id', flat=True), [])
        self.assertCountEqual(Request.get_requests_awaiting_approval(self.superuser).values_list('id', flat=True),
                              [self.request_approvalwf_1.id])

        self.request_approvalwf_2 = Request.objects.create(instance=self.instance2,
                                                           state=RequestState.SUBMITTED,
                                                           operation=self.create_operation_test)

        self.assertCountEqual(Request.get_requests_awaiting_approval(self.user1).values_list('id', flat=True),
                              [self.request_approvalwf_1.id])
        self.assertCountEqual(Request.get_requests_awaiting_approval(self.user2).values_list('id', flat=True),
                              [self.request_approvalwf_2.id])
        self.assertCountEqual(Request.get_requests_awaiting_approval(self.superuser).values_list('id', flat=True),
                              [self.request_approvalwf_1.id, self.request_approvalwf_2.id])
