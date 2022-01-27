from django.urls import reverse

from service_catalog.models import RequestState, InstanceState
from tests.test_service_catalog.base_test_request import BaseTestRequest

AUTHORIZED_STATES = [RequestState.SUBMITTED, RequestState.NEED_INFO, RequestState.REJECTED, RequestState.ACCEPTED]


class TestApiRequestCancel(BaseTestRequest):

    def setUp(self):
        super(TestApiRequestCancel, self).setUp()
        self.test_instance.state = InstanceState.AVAILABLE
        self.test_instance.save()

    def _cancel(self, status=200):
        response = self.client.post(reverse('api_request_cancel', kwargs={'pk': self.test_request.id}))
        self.assertEqual(response.status_code, status)
        if status == 200:
            self.test_request.refresh_from_db()
            self.assertEqual(self.test_request.state, RequestState.CANCELED)

    def test_admin_can_cancel_request(self):
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._cancel()

    def test_admin_cannot_cancel_request_in_forbidden_state(self):
        forbidden_state = RequestState.values
        for state in AUTHORIZED_STATES:
            forbidden_state.remove(state)
        for state in forbidden_state:
            self.test_request.state = state
            self.test_request.save()
            self._cancel(status=403)

    def test_user_can_cancel_request(self):
        self.client.force_login(self.standard_user)
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._cancel()

    def test_user_cannot_cancel_request_in_forbidden_state(self):
        self.client.force_login(self.standard_user)
        forbidden_state = RequestState.values
        for state in AUTHORIZED_STATES:
            forbidden_state.remove(state)
        for state in forbidden_state:
            self.test_request.state = state
            self.test_request.save()
            self._cancel(status=403)

    def test_cannot_cancel_request_when_logout(self):
        self.client.logout()
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._cancel(status=403)
