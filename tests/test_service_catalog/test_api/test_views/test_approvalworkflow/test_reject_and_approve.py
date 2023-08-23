from django.contrib.auth.models import User
from rest_framework.reverse import reverse

from profiles.models import Permission, Role
from service_catalog.models import ApprovalWorkflow, ApprovalStep, Instance, Request, RequestState
from tests.test_service_catalog.base import BaseTestAPI


class TestApprovalWorklowRejectApprove(BaseTestAPI):
    def setUp(self):
        super(TestApprovalWorklowRejectApprove, self).setUp()
        # Create approval workflow
        self.approval_worklflow = ApprovalWorkflow.objects.create(operation=self.create_operation_test)
        self.approval_worklflow.scopes.set([self.test_quota_scope])
        self.approval_worklflow.save()

        self.approval_step1 = ApprovalStep(name="Step 1", approval_workflow=self.approval_worklflow)
        self.approval_step1.permission = Permission.objects.get_by_natural_key(codename="can_approve_approvalstep",
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
            user=self.standard_user)

    def test_superuser_can_approve(self):
        self.client.force_login(self.superuser)
        url_approve = reverse('api_request_approval_workflow_state_approve', kwargs={'pk': self.test_request.pk})
        response = self.client.post(url_approve, format='json')
        self.test_request.refresh_from_db()
        self.assertTrue(self.test_request.state == RequestState.ACCEPTED)
        self.assertEqual(response.status_code, 200)

    def test_superuser_can_reject(self):
        self.client.force_login(self.superuser)
        url_reject = reverse('api_request_approval_workflow_state_reject', kwargs={'pk': self.test_request.pk})
        response = self.client.post(url_reject, format='json')
        self.test_request.refresh_from_db()
        self.assertTrue(self.test_request.state == RequestState.REJECTED)
        self.assertEqual(response.status_code, 200)

    def test_approver_can_approve(self):
        approver = User.objects.create(username='approver', email="approver@local.com")
        role_approver = Role.objects.create(name="Approver")
        role_approver.permissions.add(self.approval_step1.permission)
        self.test_quota_scope.add_user_in_role(approver, role_approver)
        self.client.force_login(approver)
        url_approve = reverse('api_request_approval_workflow_state_approve', kwargs={'pk': self.test_request.pk})
        response = self.client.post(url_approve, format='json')
        self.test_request.refresh_from_db()
        self.assertTrue(self.test_request.state == RequestState.ACCEPTED)
        self.assertEqual(response.status_code, 200)

    def test_approver_can_reject(self):
        approver = User.objects.create(username='approver', email="approver@local.com")
        role_approver = Role.objects.create(name="Approver")
        role_approver.permissions.add(self.approval_step1.permission)
        self.test_quota_scope.add_user_in_role(approver, role_approver)

        self.client.force_login(approver)
        url_reject = reverse('api_request_approval_workflow_state_reject', kwargs={'pk': self.test_request.pk})
        response = self.client.post(url_reject, format='json')
        self.test_request.refresh_from_db()
        self.assertTrue(self.test_request.state == RequestState.REJECTED)
        self.assertEqual(response.status_code, 200)

    def test_standard_user_cannot_approve(self):
        self.client.force_login(self.standard_user)
        url_approve = reverse('api_request_approval_workflow_state_approve', kwargs={'pk': self.test_request.pk})
        response = self.client.post(url_approve, format='json')
        self.test_request.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertTrue(self.test_request.state == RequestState.SUBMITTED)

    def test_standard_user_cannot_reject(self):
        self.client.force_login(self.standard_user)
        url_reject = reverse('api_request_approval_workflow_state_reject', kwargs={'pk': self.test_request.pk})
        response = self.client.post(url_reject, format='json')
        self.test_request.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertTrue(self.test_request.state == RequestState.SUBMITTED)
