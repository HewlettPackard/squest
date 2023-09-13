from django.urls import reverse

from service_catalog.models import RequestHook, RequestState
from tests.test_service_catalog.base import BaseTest


class RequestHooksEditViewsTest(BaseTest):

    def setUp(self):
        super(RequestHooksEditViewsTest, self).setUp()
        self.request_hook_test = RequestHook.objects.create(name="hook1",
                                                          state=RequestState.FAILED,
                                                          job_template=self.job_template_test)
        args = {
            "pk": self.request_hook_test.id
        }
        self.url = reverse('service_catalog:requesthook_edit', kwargs=args)

    def test_get_page(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_edit_request_hook(self):
        data = {
            "name": "hook2",
            "state": RequestState.COMPLETE,
            "job_template": self.job_template_test.id,
            "extra_vars": {}
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(302, response.status_code)
        self.request_hook_test.refresh_from_db()
        self.assertEqual(self.request_hook_test.name, "hook2")
        self.assertEqual(self.request_hook_test.state, RequestState.COMPLETE)
