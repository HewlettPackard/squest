from django.urls import reverse

from service_catalog.models import RequestHook, RequestState
from tests.test_service_catalog.base import BaseTest


class RequestHooksCreateViewsTest(BaseTest):

    def setUp(self):
        super(RequestHooksCreateViewsTest, self).setUp()
        self.url = reverse('service_catalog:requesthook_create')
        self.number_request_hook_before = RequestHook.objects.all().count()

    def test_get_page(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_create_valid_request_hook(self):
        data = {
            "name": "hook1",
            "state": RequestState.FAILED,
            "job_template": self.job_template_test.id,
            "extra_vars": "{}"
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(self.number_request_hook_before + 1, RequestHook.objects.all().count())


    def test_create_valid_model_invalid_state(self):
        data = {
            "name": "hook1",
            "state": "non_valid_state",
            "job_template": self.job_template_test.id,
            "extra_vars": "{}"
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.number_request_hook_before, RequestHook.objects.all().count())
        self.assertContains(response, "Select a valid choice", status_code=200, html=False)
