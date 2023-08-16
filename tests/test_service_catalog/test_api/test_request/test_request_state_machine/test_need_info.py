from django.urls import reverse

from service_catalog.models import RequestState
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


AUTHORIZED_STATES = [RequestState.SUBMITTED]

class TestApiRequestNeedInfo(BaseTestRequestAPI):

    def setUp(self):
        super(TestApiRequestNeedInfo, self).setUp()
        self.need_info_url = reverse('api_request_need_info', kwargs={'pk': self.test_request.id})

    def _need_info(self, status=200, data=None):
        message_count = self.test_request.comments.count()
        response = self.client.post(reverse('api_request_need_info', kwargs={'pk': self.test_request.id}), data=data)
        self.assertEqual(response.status_code, status)
        if status == 200:
            self.test_request.refresh_from_db()
            self.assertEqual(self.test_request.state, RequestState.NEED_INFO)
            last_message = self.test_request.comments.order_by("-creation_date").first()
            if data:
                self.assertEqual(data["content"], last_message.content)
                self.assertEqual(response.wsgi_request.user, last_message.sender)
                self.assertEqual(self.test_request.comments.count(), message_count + 1)
            else:
                self.assertEqual(self.test_request.comments.count(), message_count)

    def test_admin_can_ask_need_info_request_with_comment(self):
        data = {"content": "test comment"}
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._need_info(data=data)

    def test_admin_can_ask_need_info_request_without_comment(self):
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._need_info()

    def test_admin_cannot_ask_need_info_request_in_forbidden_state(self):
        forbidden_state = RequestState.values
        for state in AUTHORIZED_STATES:
            forbidden_state.remove(state)
        for state in forbidden_state:
            self.test_request.state = state
            self.test_request.save()
            self._need_info(status=403)

    def test_user_cannot_ask_need_info_request(self):
        self.client.force_login(self.standard_user)
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._need_info(status=403)

    def test_cannot_ask_need_info_request_when_logout(self):
        self.client.logout()
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._need_info(status=403)
