from django.urls import reverse

from service_catalog.models import InstanceHook, InstanceState
from tests.test_service_catalog.base import BaseTest


class InstanceHooksEditViewsTest(BaseTest):

    def setUp(self):
        super(InstanceHooksEditViewsTest, self).setUp()
        self.instance_hook_test = InstanceHook.objects.create(name="hook1",
                                                          state=InstanceState.PROVISIONING,
                                                          job_template=self.job_template_test)
        args = {
            "pk": self.instance_hook_test.id
        }
        self.url = reverse('service_catalog:instancehook_edit', kwargs=args)

    def test_get_page(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_edit_instance_hook(self):
        data = {
            "name": "hook2",
            "state": InstanceState.PENDING,
            "job_template": self.job_template_test.id,
            "extra_vars": {}
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(302, response.status_code)
        self.instance_hook_test.refresh_from_db()
        self.assertEqual(self.instance_hook_test.name, "hook2")
        self.assertEqual(self.instance_hook_test.state, InstanceState.PENDING)
