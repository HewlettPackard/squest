from unittest import mock

from service_catalog.models import GlobalHook, Request, Instance, InstanceState, RequestState
from service_catalog.models.state_hooks import HookManager
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestStateHook(BaseTestRequest):

    def setUp(self):
        super(TestStateHook, self).setUp()

        self.global_hook1 = GlobalHook.objects.create(name="global-hook1",
                                                      model="Request",
                                                      state=RequestState.ACCEPTED,
                                                      job_template=self.job_template_test,
                                                      extra_vars={"key1": "value1"})

        self.global_hook2 = GlobalHook.objects.create(name="global-hook2",
                                                      model="Instance",
                                                      state=InstanceState.PROVISIONING,
                                                      job_template=self.job_template_test,
                                                      extra_vars={"key2": "value2"})

        self.global_hook3 = GlobalHook.objects.create(name="global-hook3",
                                                      model="Instance",
                                                      state=InstanceState.DELETING,
                                                      service=self.service_test,
                                                      job_template=self.job_template_test,
                                                      extra_vars={"key3": "value3"})

    def test_hook_manager_called(self):
        with mock.patch("service_catalog.models.state_hooks.HookManager.trigger_hook") as mock_trigger_hook:
            self.test_request.accept()
            self.test_request.save()
            self.assertEqual(mock_trigger_hook.call_count, 1)

            self.test_instance.provisioning()
            self.test_instance.save()
            self.assertEqual(mock_trigger_hook.call_count, 2)

    def test_hook_manager_called_on_create_object(self):
        with mock.patch("service_catalog.models.state_hooks.HookManager.trigger_hook") as mock_trigger_hook1:
            Request.objects.create(fill_in_survey={},
                                   instance=self.test_instance,
                                   operation=self.create_operation_test,
                                   user=self.standard_user)
            mock_trigger_hook1.assert_called()
        with mock.patch("service_catalog.models.state_hooks.HookManager.trigger_hook") as mock_trigger_hook2:
            Instance.objects.create(name="test_instance_1",
                                    service=self.service_test,
                                    spoc=self.standard_user)
            mock_trigger_hook2.assert_called()

    def test_hook_manager_execute_job_template(self):
        from service_catalog.api.serializers import InstanceReadSerializer, RequestSerializer
        with mock.patch("service_catalog.models.job_templates.JobTemplate.execute") as mock_job_template_execute:

            HookManager.trigger_hook(sender=Request, instance=self.test_request,
                                     name="accept", source=RequestState.SUBMITTED, target=RequestState.ACCEPTED)
            expected_extra_vars = self.global_hook1.extra_vars
            expected_extra_vars["squest"] = RequestSerializer(self.test_request).data
            mock_job_template_execute.assert_called_with(extra_vars=expected_extra_vars)

        with mock.patch("service_catalog.models.job_templates.JobTemplate.execute") as mock_job_template_execute2:
            HookManager.trigger_hook(sender=Instance, instance=self.test_instance,
                                     name="accept", source=InstanceState.PENDING, target=InstanceState.PROVISIONING)
            expected_extra_vars = self.global_hook2.extra_vars
            expected_extra_vars["squest"] = InstanceReadSerializer(self.test_instance).data
            mock_job_template_execute2.assert_called_with(extra_vars=expected_extra_vars)

    def test_hook_manager_does_not_execute_job_template(self):
        with mock.patch("service_catalog.models.job_templates.JobTemplate.execute") as mock_job_template_execute:
            HookManager.trigger_hook(sender=Request, instance=self.test_request,
                                     name="reject", source=RequestState.SUBMITTED, target=RequestState.REJECTED)
            mock_job_template_execute.assert_not_called()

        with mock.patch("service_catalog.models.job_templates.JobTemplate.execute") as mock_job_template_execute2:
            HookManager.trigger_hook(sender=Instance, instance=self.test_instance,
                                     name="available", source=InstanceState.PROVISIONING,
                                     target=InstanceState.AVAILABLE)
            mock_job_template_execute2.mock_job_template_execute2()

    def test_hook_manager_execute_job_template_on_selected_service(self):
        instance = Instance.objects.create(
            name="test_instance_1",
            service=self.service_test,
            spoc=self.standard_user
        )
        with mock.patch("service_catalog.models.job_templates.JobTemplate.execute") as mock_job_template_execute_1:
            # test with correct service and target state. Hook executed
            HookManager.trigger_hook(sender=Instance, instance=instance,
                                     name="delete", source=InstanceState.AVAILABLE, target=InstanceState.DELETING)
            mock_job_template_execute_1.assert_called()

        with mock.patch("service_catalog.models.job_templates.JobTemplate.execute") as mock_job_template_execute_2:
            # test with correct service and wrong  target state. Hook not executed
            HookManager.trigger_hook(sender=Instance, instance=instance,
                                     name="process", source=InstanceState.PENDING, target=InstanceState.AVAILABLE)
            mock_job_template_execute_2.assert_not_called()

        with mock.patch("service_catalog.models.job_templates.JobTemplate.execute") as mock_job_template_execute_3:
            # test with correct wrong service and correct target state. Hook not executed
            instance.service = self.service_test_2
            instance.save()
            HookManager.trigger_hook(sender=Instance, instance=instance,
                                     name="delete", source=InstanceState.AVAILABLE, target=InstanceState.DELETING)
            mock_job_template_execute_3.assert_not_called()
