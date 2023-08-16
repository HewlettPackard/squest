from django.urls import reverse

from service_catalog.models import RequestState
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI

AUTHORIZED_STATES = [RequestState.COMPLETE]


class TestApiRequestArchive(BaseTestRequestAPI):

    def setUp(self):
        super(TestApiRequestArchive, self).setUp()

    def _archive(self, status=200):
        response = self.client.post(reverse('api_request_archive', kwargs={'pk': self.test_request.id}))
        self.assertEqual(response.status_code, status)
        if status == 200:
            self.test_request.refresh_from_db()
            self.assertEqual(self.test_request.state, RequestState.ARCHIVED)

    def test_admin_can_archive_request(self):
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._archive()


    def test_admin_cannot_archive_request_in_forbidden_state(self):
        forbidden_state = RequestState.values
        for state in AUTHORIZED_STATES:
            forbidden_state.remove(state)
        for state in forbidden_state:
            self.test_request.state = state
            self.test_request.save()
            self._archive(status=403)

    def test_user_cannot_archive_request(self):
        self.client.force_login(self.standard_user)
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._archive(status=403)

    def test_cannot_archive_request_when_logout(self):
        self.client.logout()
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._archive(status=403)
