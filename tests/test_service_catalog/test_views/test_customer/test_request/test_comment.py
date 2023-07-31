from django.urls import reverse

from service_catalog.models import RequestMessage
from tests.test_service_catalog.base_test_request import BaseTestRequest


class CustomerRequestCommentTest(BaseTestRequest):

    def setUp(self):
        super(CustomerRequestCommentTest, self).setUp()
        # add one comment
        self.comment = RequestMessage.objects.create(sender=self.standard_user,
                                                     request=self.test_request,
                                                     content="first test message")
        request = {
            'request_id': self.test_request.id
        }
        comment = {
            'pk': self.comment.id
        }
        self.data_to_edit = {"content": "comment edited"}
        self.create_url = reverse('service_catalog:requestmessage_create', kwargs=request)
        self.edit_url = reverse('service_catalog:requestmessage_edit', kwargs={**request, **comment})

    def _assert_can_list_comment(self):
        response = self.client.get(self.create_url)
        self.assertEqual(200, response.status_code)
        self.assertTrue("messages" in response.context)
        self.assertEqual(1, len(response.context["messages"]))

    def _assert_can_add_comment(self):
        number_message_before = RequestMessage.objects.filter(request=self.test_request).count()
        data = {
            "content": "new message"
        }
        response = self.client.post(self.create_url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(number_message_before + 1,
                         RequestMessage.objects.filter(request=self.test_request).count())

    def test_cannot_get_comment_list_when_logout(self):
        self.client.logout()
        response = self.client.get(self.create_url)
        self.assertEqual(302, response.status_code)

    def test_admin_can_list_request_comment(self):
        self._assert_can_list_comment()

    def test_non_owner_cannot_list_request_comment(self):
        self.client.login(username=self.standard_user_2, password=self.common_password)
        args = {
            'request_id': self.test_request.id
        }
        url = reverse('service_catalog:requestmessage_create', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

    def test_admin_can_add_request_message(self):
        self._assert_can_add_comment()

    def test_non_owner_cannot_add_request_message(self):
        self.client.login(username=self.standard_user_2, password=self.common_password)
        data = {
            "content": "new message"
        }
        response = self.client.post(self.create_url, data=data)
        self.assertEqual(403, response.status_code)

    def test_sender_can_edit_comment(self):
        self.client.force_login(user=self.standard_user)
        response = self.client.post(self.edit_url, data=self.data_to_edit)
        self.assertEqual(302, response.status_code)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "comment edited")
        self.assertEqual(self.comment.sender, self.standard_user)

    def test_admin_cannot_edit_user_comment(self):
        self.client.force_login(self.superuser)
        response = self.client.post(self.edit_url, data=self.data_to_edit)
        self.assertEqual(403, response.status_code)

    def test_non_sender_cannot_edit_comment(self):
        self.client.force_login(self.standard_user_2)
        response = self.client.post(self.edit_url, data=self.data_to_edit)
        self.assertEqual(403, response.status_code)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "first test message")
        self.assertEqual(self.comment.sender, self.standard_user)

    def test_cannot_edit_comment_when_logout(self):
        self.client.logout()
        response = self.client.post(self.edit_url, data=self.data_to_edit)
        self.assertEqual(302, response.status_code)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "first test message")
        self.assertEqual(self.comment.sender, self.standard_user)
