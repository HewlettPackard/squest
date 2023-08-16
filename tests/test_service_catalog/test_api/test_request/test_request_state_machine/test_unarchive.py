from django.urls import reverse

from service_catalog.models import RequestState
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


AUTHORIZED_STATES = [RequestState.ARCHIVED]


class TestApiRequestUnarchive(BaseTestRequestAPI):

    def setUp(self):
        super(TestApiRequestUnarchive, self).setUp()

    def _unarchive(self, status=200):
        response = self.client.post(reverse('api_request_unarchive', kwargs={'pk': self.test_request.id}))
        self.assertEqual(response.status_code, status)
        if status == 200:
            self.test_request.refresh_from_db()
            self.assertEqual(self.test_request.state, RequestState.COMPLETE)

    def test_admin_can_unarchive_request(self):
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._unarchive()

    def test_admin_cannot_unarchive_request_in_forbidden_state(self):
        forbidden_state = RequestState.values
        for state in AUTHORIZED_STATES:
            forbidden_state.remove(state)
        for state in forbidden_state:
            self.test_request.state = state
            self.test_request.save()
            self._unarchive(status=403)

    def test_user_cannot_unarchive_request(self):
        self.client.force_login(self.standard_user)
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._unarchive(status=403)

    def test_cannot_unarchive_request_when_logout(self):
        self.client.logout()
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._unarchive(status=403)
