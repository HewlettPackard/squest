from django.urls import reverse

from service_catalog.models import RequestState
from tests.test_service_catalog.base_test_request import BaseTestRequest


AUTHORIZED_STATES = [RequestState.SUBMITTED, RequestState.ACCEPTED, RequestState.NEED_INFO]


class TestApiRequestReject(BaseTestRequest):

    def setUp(self):
        super(TestApiRequestReject, self).setUp()

    def _reject(self, status=200, data=None):
        message_count = self.test_request.comments.count()
        response = self.client.post(reverse('api_request_reject', kwargs={'pk': self.test_request.id}), data=data)
        self.assertEqual(response.status_code, status)
        if status == 200:
            self.test_request.refresh_from_db()
            self.assertEqual(self.test_request.state, RequestState.REJECTED)
            last_message = self.test_request.comments.order_by("-creation_date").first()
            if data:
                self.assertEqual(data["content"], last_message.content)
                self.assertEqual(response.wsgi_request.user, last_message.sender)
                self.assertEqual(self.test_request.comments.count(), message_count + 1)
            else:
                self.assertEqual(self.test_request.comments.count(), message_count)

    def test_admin_can_reject_request_without_comment(self):
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._reject()

    def test_admin_can_reject_request_with_comment(self):
        data = {"content": "test comment"}
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._reject(data=data)

    def test_admin_cannot_reject_request_in_forbidden_state(self):
        forbidden_state = RequestState.values
        forbidden_state.remove(RequestState.SUBMITTED)
        forbidden_state.remove(RequestState.ACCEPTED)
        forbidden_state.remove(RequestState.NEED_INFO)
        for state in forbidden_state:
            self.test_request.state = state
            self.test_request.save()
            self._reject(status=403)

    def test_user_cannot_reject_request(self):
        self.client.force_login(self.standard_user)
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._reject(status=403)

    def test_cannot_reject_request_when_logout(self):
        self.client.logout()
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._reject(status=403)
