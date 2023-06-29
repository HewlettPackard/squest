from django.urls import reverse

from service_catalog.models import GlobalHook
from tests.test_service_catalog.base import BaseTest


class GlobalHooksEditViewsTest(BaseTest):

    def setUp(self):
        super(GlobalHooksEditViewsTest, self).setUp()
        self.global_hook_test = GlobalHook.objects.create(name="hook1",
                                                          model="Instance",
                                                          state="PROVISIONING",
                                                          job_template=self.job_template_test)
        args = {
            "globalhook_id": self.global_hook_test.id
        }
        self.url = reverse('service_catalog:globalhook_edit', kwargs=args)

    def test_get_page(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_edit_global_hook(self):
        data = {
            "name": "hook2",
            "model": "Instance",
            "state": "PENDING",
            "job_template": self.job_template_test.id,
            "extra_vars": {}
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(302, response.status_code)
        self.global_hook_test.refresh_from_db()
        self.assertEqual(self.global_hook_test.name, "hook2")
        self.assertEqual(self.global_hook_test.state, "PENDING")
