from django.urls import reverse

from service_catalog.models import RequestHook, RequestState
from tests.test_service_catalog.base import BaseTest


class RequestHookDeleteViewsTest(BaseTest):

    def setUp(self):
        super(RequestHookDeleteViewsTest, self).setUp()
        self.request_hook_test = RequestHook.objects.create(name="hook1",
                                                          state=RequestState.FAILED,
                                                          job_template=self.job_template_test)
        args = {
            "pk": self.request_hook_test.id
        }
        self.url = reverse('service_catalog:requesthook_delete', kwargs=args)

    def test_can_delete_request_hook(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

        id_to_delete = self.request_hook_test.id
        response = self.client.post(self.url)
        self.assertEqual(302, response.status_code)
        self.assertFalse(RequestHook.objects.filter(id=id_to_delete).exists())

    def test_cannot_delete_request_hook_when_logout(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(302, response.status_code)
