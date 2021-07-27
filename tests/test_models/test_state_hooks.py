from unittest import mock

from service_catalog.models import GlobalHook, Request, Instance
from service_catalog.models.state_hooks import HookManager
from tests.base_test_request import BaseTestRequest


class TestStateHook(BaseTestRequest):

    def setUp(self):
        super(TestStateHook, self).setUp()

        self.global_hook1 = GlobalHook.objects.create(name="global-hook1",
                                                      model="Request",
                                                      state="ACCEPTED",
                                                      job_template=self.job_template_test,
                                                      extra_vars={"key1": "value1"})

        self.global_hook2 = GlobalHook.objects.create(name="global-hook2",
                                                      model="Instance",
                                                      state="PROVISIONING",
                                                      job_template=self.job_template_test,
                                                      extra_vars={"key2": "value2"})

    def test_hook_manager_called(self):
        with mock.patch("service_catalog.models.state_hooks.HookManager.trigger_hook") as mock_trigger_hook:
            self.test_request.accept()
            self.test_request.save()
            self.assertEquals(mock_trigger_hook.call_count, 1)

            self.test_instance.provisioning()
            self.test_instance.save()
            self.assertEquals(mock_trigger_hook.call_count, 2)

    def test_hook_manager_execute_job_template(self):
        from service_catalog.serializers.instance_serializer import InstanceSerializer
        from service_catalog.serializers.request_serializer import RequestSerializer
        with mock.patch("service_catalog.models.job_templates.JobTemplate.execute") as mock_job_template_execute:

            HookManager.trigger_hook(sender=Request, instance=self.test_request,
                                     name="accept", source="SUBMITTED", target="ACCEPTED")
            expected_extra_vars = self.global_hook1.extra_vars
            expected_extra_vars["squest"] = RequestSerializer(self.test_request).data
            mock_job_template_execute.assert_called_with(extra_vars=expected_extra_vars)

            HookManager.trigger_hook(sender=Instance, instance=self.test_instance,
                                     name="accept", source="PENDING", target="PROVISIONING")
            expected_extra_vars = self.global_hook2.extra_vars
            expected_extra_vars["squest"] = InstanceSerializer(self.test_instance).data
            mock_job_template_execute.assert_called_with(extra_vars=expected_extra_vars)

    def test_hook_manager_does_not_execute_job_template(self):
        with mock.patch("service_catalog.models.job_templates.JobTemplate.execute") as mock_job_template_execute:
            HookManager.trigger_hook(sender=Request, instance=self.test_request,
                                     name="reject", source="SUBMITTED", target="REJECTED")
            mock_job_template_execute.assert_not_called()

            HookManager.trigger_hook(sender=Instance, instance=self.test_instance,
                                     name="available", source="PROVISIONING", target="AVAILABLE")
            mock_job_template_execute.assert_not_called()
