from django.core.exceptions import PermissionDenied
from django.urls import reverse

from service_catalog.models import Request, RequestMessage
from tests.base_test_request import BaseTestRequest


class CustomerRequestCommentTest(BaseTestRequest):

    def setUp(self):
        super(CustomerRequestCommentTest, self).setUp()
        # add one comment
        RequestMessage.objects.create(sender=self.standard_user,
                                      request=self.test_request,
                                      content="first test message")
        args = {
            'request_id': self.test_request.id
        }
        self.url = reverse('service_catalog:customer_request_comment', kwargs=args)

    def _assert_can_list_comment(self):
        response = self.client.get(self.url)
        self.assertEquals(200, response.status_code)
        self.assertTrue("messages" in response.context)
        self.assertEquals(1, len(response.context["messages"]))

    def _assert_can_add_comment(self):
        number_message_before = RequestMessage.objects.filter(request=self.test_request).count()
        data = {
            "content": "new message"
        }
        response = self.client.post(self.url, data=data)
        self.assertEquals(302, response.status_code)
        self.assertEquals(number_message_before + 1,
                          RequestMessage.objects.filter(request=self.test_request).count())

    def test_admin_can_list_request_comment(self):
        self._assert_can_list_comment()

    def test_request_owner_can_list_request_comment(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        self._assert_can_list_comment()

    def test_non_owner_cannot_list_request_comment(self):
        self.client.login(username=self.standard_user_2, password=self.common_password)
        args = {
            'request_id': self.test_request.id
        }
        url = reverse('service_catalog:customer_request_comment', kwargs=args)
        response = self.client.get(url)
        self.assertEquals(403, response.status_code)

    def test_admin_can_add_request_message(self):
        self._assert_can_add_comment()

    def test_owner_can_add_request_message(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        self._assert_can_add_comment()

    def test_non_owner_cannot_add_request_message(self):
        self.client.login(username=self.standard_user_2, password=self.common_password)
        data = {
            "content": "new message"
        }
        response = self.client.post(self.url, data=data)
        self.assertEquals(403, response.status_code)
