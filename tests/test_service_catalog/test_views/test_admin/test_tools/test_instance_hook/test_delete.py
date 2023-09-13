from django.urls import reverse

from service_catalog.models import InstanceHook, InstanceState
from tests.test_service_catalog.base import BaseTest


class InstanceHookDeleteViewsTest(BaseTest):

    def setUp(self):
        super(InstanceHookDeleteViewsTest, self).setUp()
        self.instance_hook_test = InstanceHook.objects.create(name="hook1",
                                                          state=InstanceState.PROVISIONING,
                                                          job_template=self.job_template_test)
        args = {
            "pk": self.instance_hook_test.id
        }
        self.url = reverse('service_catalog:instancehook_delete', kwargs=args)

    def test_can_delete_instance_hook(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

        id_to_delete = self.instance_hook_test.id
        response = self.client.post(self.url)
        self.assertEqual(302, response.status_code)
        self.assertFalse(InstanceHook.objects.filter(id=id_to_delete).exists())

    def test_cannot_delete_instance_hook_when_logout(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(302, response.status_code)
