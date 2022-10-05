from django.urls import reverse
from service_catalog.models import RequestMessage
from service_catalog.models.approval_step_state import ApprovalStepState
from service_catalog.models.approval_state import ApprovalState
from service_catalog.models.instance import InstanceState
from service_catalog.models.request import RequestState
from tests.test_service_catalog.base_approval import BaseApproval


class RequestApprovalStepViewTest(BaseApproval):

    def _accept_request_with_expected_state(self, expected_request_state, expected_instance_state, user, team,
                                            data=None, status=302):
        args = {
            'request_id': self.test_request.id
        }
        if data is None:
            data = {
                'squest_instance_name': self.test_request.instance.name,
                'billing_group_id': '',
                'text_variable': 'my_var',
                'multiplechoice_variable': 'choice1',
                'multiselect_var': 'multiselect_1',
                'textarea_var': '2',
                'password_var': 'password1234',
                'integer_var': '1',
                'float_var': '0.6'
            }
        url = reverse('service_catalog:admin_request_accept', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        approval_step_state = ApprovalStepState.objects.get(
            team=team,
            request=self.test_request,
            approval_step=self.test_request.approval_step
        )
        response = self.client.post(url, data=data)
        self.assertEqual(status, response.status_code)
        self.test_request.refresh_from_db()
        self.assertEqual(self.test_request.state, expected_request_state)
        self.test_instance.refresh_from_db()
        self.assertEqual(self.test_instance.state, expected_instance_state)
        if response.status_code == 302:
            approval_step_state.refresh_from_db()
            self.assertEqual(self.test_request.accepted_by, user)
            self.assertEqual(approval_step_state.state, ApprovalState.APPROVED)
            self.assertEqual(approval_step_state.updated_by, user)
            billing_group_id = '' if not self.test_request.instance.billing_group else self.test_request.instance.billing_group.id
            self.assertEqual(data['billing_group_id'], billing_group_id)

    def test_approver_can_reject_request(self):
        self.client.force_login(self.my_user)
        args = {
            'request_id': self.test_request.id
        }
        url = reverse('service_catalog:admin_request_reject', kwargs=args)
        data = {
            "content": "admin message"
        }
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.test_request.refresh_from_db()
        self.assertEqual(self.test_request.state, RequestState.REJECTED)
        self.assertEqual(1, RequestMessage.objects.filter(request=self.test_request.id).count())
        rejected_expected = ApprovalStepState.objects.get(
            team=self.test_team2,
            request=self.test_request,
            approval_step=self.test_request.approval_step,
            updated_by=self.my_user
        )
        pending_expected = ApprovalStepState.objects.filter(
            request=self.test_request,
            approval_step=self.test_request.approval_step
        ).exclude(team=self.test_team2)
        self.assertEqual(rejected_expected.state, ApprovalState.REJECTED)
        self.assertEqual(pending_expected.count(), 1)
        for expected in pending_expected:
            self.assertEqual(expected.state, ApprovalState.PENDING)

    def test_non_approver_cannot_reject_request(self):
        self.client.force_login(self.superuser)
        args = {
            'request_id': self.test_request.id
        }
        url = reverse('service_catalog:admin_request_reject', kwargs=args)
        data = {
            "content": "admin message"
        }
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        response = self.client.post(url, data=data)
        self.assertEqual(403, response.status_code)
        self.test_request.refresh_from_db()
        self.assertEqual(self.test_request.state, RequestState.SUBMITTED)

    def test_one_approver_must_approve_for_at_least_one_type(self):
        self.client.force_login(self.my_user)
        self._accept_request_with_expected_state(expected_request_state=RequestState.SUBMITTED,
                                                 expected_instance_state=InstanceState.PENDING,
                                                 user=self.my_user, team=self.test_team2)
        self.assertEqual(self.test_request.approval_step, self.test_approval_step_2)

    def test_all_approvers_must_approve_for_all_of_them_type(self):
        self.test_request.approval_step = self.test_approval_step_2
        self.test_request.save()
        self.client.force_login(self.my_user)
        self._accept_request_with_expected_state(expected_request_state=RequestState.SUBMITTED,
                                                 expected_instance_state=InstanceState.PENDING,
                                                 user=self.my_user, team=self.test_team2)
        self.assertEqual(self.test_request.approval_step, self.test_approval_step_2)
        self.client.force_login(self.my_user2)
        self._accept_request_with_expected_state(expected_request_state=RequestState.SUBMITTED,
                                                 expected_instance_state=InstanceState.PENDING,
                                                 user=self.my_user2, team=self.test_team)
        self.assertEqual(self.test_request.approval_step, self.test_approval_step_3)
