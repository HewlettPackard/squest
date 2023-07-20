from django.urls import reverse

from service_catalog.models import RequestState
from tests.test_service_catalog.base_test_request import BaseTestRequest


AUTHORIZED_STATES = [RequestState.NEED_INFO, RequestState.REJECTED]


class TestApiRequestReSubmit(BaseTestRequest):

    def setUp(self):
        super(TestApiRequestReSubmit, self).setUp()

    def _re_submit(self, status=200, data=None):
        message_count = self.test_request.comments.count()
        response = self.client.post(reverse('api_request_re_submit', kwargs={'pk': self.test_request.id}), data=data)
        self.assertEqual(response.status_code, status)
        if status == 200:
            self.test_request.refresh_from_db()
            self.assertEqual(self.test_request.state, RequestState.SUBMITTED)
            last_message = self.test_request.comments.order_by("-creation_date").first()
            if data:
                self.assertEqual(data["content"], last_message.content)
                self.assertEqual(response.wsgi_request.user, last_message.sender)
                self.assertEqual(self.test_request.comments.count(), message_count + 1)
            else:
                self.assertEqual(self.test_request.comments.count(), message_count)

    def test_admin_can_re_submit_request_without_comment(self):
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._re_submit()

    def test_admin_can_re_submit_request_with_comment(self):
        data = {"content": "test comment"}
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._re_submit(data=data)

    def test_admin_cannot_re_submit_request_in_forbidden_state(self):
        forbidden_state = RequestState.values
        for state in AUTHORIZED_STATES:
            forbidden_state.remove(state)
        for state in forbidden_state:
            self.test_request.state = state
            self.test_request.save()
            self._re_submit(status=403)

    def test_user_cannot_re_submit_request(self):
        self.client.force_login(self.standard_user)
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._re_submit(status=403)

    def test_cannot_re_submit_request_when_logout(self):
        self.client.logout()
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._re_submit(status=403)
