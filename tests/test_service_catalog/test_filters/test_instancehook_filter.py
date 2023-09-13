from service_catalog.filters.global_hook_filter import InstanceHookFilter, RequestHookFilter
from service_catalog.models import InstanceHook, RequestState, InstanceState, RequestHook
from tests.test_service_catalog.base import BaseTest


class TestInstanceHooksFilter(BaseTest):
    def setUp(self):
        super(TestInstanceHooksFilter, self).setUp()
        self.global_hook1 = RequestHook.objects.create(name="global-hook1",
                                                      state=RequestState.ACCEPTED,
                                                      job_template=self.job_template_test,
                                                      extra_vars={"key1": "value1"})
        self.global_hook2 = InstanceHook.objects.create(name="global-hook2",
                                                      state=InstanceState.PROVISIONING,
                                                      job_template=self.job_template_test,
                                                      extra_vars={"key2": "value2"})
        self.global_hook3 = RequestHook.objects.create(name="global-hook3",
                                                      state=RequestState.REJECTED,
                                                      job_template=self.job_template_test,
                                                      extra_vars={"key3": "value3"})

        self.global_hook4 = InstanceHook.objects.create(name="global-hook4",
                                                      state=InstanceState.AVAILABLE,
                                                      job_template=self.job_template_test,
                                                      extra_vars={"key4": "value4"})

    def test_filter_by_instance_state(self):
        data = {
            'state': InstanceState.AVAILABLE,
        }
        hook_filter = InstanceHookFilter(data)
        self.assertTrue(hook_filter.form.is_valid())
        self.assertEqual(1, hook_filter.qs.count())
        self.assertEqual(self.global_hook4, hook_filter.qs[0])

    def test_filter_by_request_state(self):
        data = {
            'state': RequestState.REJECTED
        }
        hook_filter = RequestHookFilter(data)
        self.assertTrue(hook_filter.form.is_valid())
        self.assertEqual(1, hook_filter.qs.count())
        self.assertEqual(self.global_hook3, hook_filter.qs[0])
