from django.contrib.auth.models import User
from rest_framework.reverse import reverse

from profiles.models import Permission, Role
from service_catalog.models import ApprovalWorkflow, ApprovalStep, Instance, Request, RequestState
from tests.test_service_catalog.base import BaseTestAPI
from tests.test_service_catalog.base_test_approval import BaseTestApprovalAPI


class TestApprovalWorkflowUpdateStepsPosition(BaseTestApprovalAPI):

    def setUp(self):
        super(TestApprovalWorkflowUpdateStepsPosition, self).setUp()
        self.url = reverse('approvalworkflow_update_steps_position', args=[self.test_approval_workflow.id])

        # approval
        self.test_approval_workflow_2 = ApprovalWorkflow.objects.create(name="test_approval_workflow_2",
                                                                        operation=self.update_operation_test)

        self.test_approval_step_3 = ApprovalStep.objects.create(name="test_approval_step_3",
                                                                approval_workflow=self.test_approval_workflow_2)

    def _assert_position_updated(self):
        self.test_approval_step_1.refresh_from_db()
        self.test_approval_step_2.refresh_from_db()
        self.assertEqual(1, self.test_approval_step_1.position)
        self.assertEqual(0, self.test_approval_step_2.position)

    def _assert_position_still_the_same(self):
        self.test_approval_step_1.refresh_from_db()
        self.test_approval_step_2.refresh_from_db()
        self.assertEqual(0, self.test_approval_step_1.position)
        self.assertEqual(1, self.test_approval_step_2.position)

    def test_set_position(self):
        data = [
            {"id": self.test_approval_step_1.id, "position": 1},
            {"id": self.test_approval_step_2.id, "position": 0},
        ]
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, 200)
        self._assert_position_updated()

    def test_set_position_invalid_step_id(self):
        data = [
            {"id": self.test_approval_step_1.id, "position": 1},
            {"id": self.test_approval_step_3.id, "position": 0},
        ]
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid Step Id For The Approval Workflow", response.data[0].title())
        self._assert_position_still_the_same()

    def test_set_position_missing_step(self):
        data = [
            {"id": self.test_approval_step_1.id, "position": 1},
        ]
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing Position", response.data[0].title())
        self._assert_position_still_the_same()

    def test_set_position_missing_position(self):
        data = [
            {"id": self.test_approval_step_1.id, "position": 0},
            {"id": self.test_approval_step_2.id, "position": 2},
        ]
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing Position 1", response.data[0].title())
        self._assert_position_still_the_same()


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
        data = {
            'text_variable': 'my_var',
            'multiplechoice_variable': 'choice1', 'multiselect_var': 'multiselect_1',
            'textarea_var': '2',
            'password_var': 'pass',
            'integer_var': '1',
            'float_var': '0.6'
        }
        self.test_request = Request.objects.create(fill_in_survey=data,
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
