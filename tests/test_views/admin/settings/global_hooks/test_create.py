from django.urls import reverse

from service_catalog.models import GlobalHook
from tests.base import BaseTest


class GlobalHooksCreateViewsTest(BaseTest):

    def setUp(self):
        super(GlobalHooksCreateViewsTest, self).setUp()
        self.url = reverse('service_catalog:global_hook_create')
        self.number_global_hook_before = GlobalHook.objects.all().count()

    def test_create_valid_global_hook(self):
        data = {
            "name": "hook1",
            "model": "Instance",
            "state": "PROVISIONING",
            "job_template": self.job_template_test.id,
            "extra_vars": "{}"
        }
        response = self.client.post(self.url, data=data)
        self.assertEquals(302, response.status_code)
        self.assertEquals(self.number_global_hook_before + 1, GlobalHook.objects.all().count())

    def test_create_invalid_model(self):
        data = {
            "name": "hook1",
            "model": "NonValidModel",
            "state": "PROVISIONING",
            "job_template": self.job_template_test.id,
            "extra_vars": "{}"
        }
        response = self.client.post(self.url, data=data)
        self.assertEquals(200, response.status_code)
        self.assertEquals(self.number_global_hook_before, GlobalHook.objects.all().count())
        self.assertContains(response, "Select a valid choice", status_code=200, html=False)

    def test_create_valid_model_invalid_state(self):
        data = {
            "name": "hook1",
            "model": "Instance",
            "state": "non_valid_state",
            "job_template": self.job_template_test.id,
            "extra_vars": "{}"
        }
        response = self.client.post(self.url, data=data)
        self.assertEquals(200, response.status_code)
        self.assertEquals(self.number_global_hook_before, GlobalHook.objects.all().count())
        self.assertContains(response, "Select a valid choice", status_code=200, html=False)

    def test_create_valid_model_valid_state_from_other_model(self):
        data1 = {
            "name": "hook1",
            "model": "Instance",
            "state": "ACCEPTED",
            "job_template": self.job_template_test.id,
            "extra_vars": "{}"
        }

        data2 = {
            "name": "hook2",
            "model": "Request",
            "state": "PENDING",
            "job_template": self.job_template_test.id,
            "extra_vars": "{}"
        }

        to_be_tested = [data1, data2]

        for data in to_be_tested:
            response = self.client.post(self.url, data=data)
            self.assertEquals(200, response.status_code)
            self.assertEquals(self.number_global_hook_before, GlobalHook.objects.all().count())
            self.assertContains(response, "is not a valid state of model", status_code=200, html=False)
