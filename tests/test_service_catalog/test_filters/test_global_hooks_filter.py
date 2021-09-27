from service_catalog.filters.global_hook_filter import GlobalHookFilter
from service_catalog.models import GlobalHook, RequestState, InstanceState
from tests.test_service_catalog.base import BaseTest


class TestGlobalHooksFilter(BaseTest):
    def setUp(self):
        super(TestGlobalHooksFilter, self).setUp()
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
                                                      model="Request",
                                                      state=RequestState.REJECTED,
                                                      job_template=self.job_template_test,
                                                      extra_vars={"key3": "value3"})

        self.global_hook4 = GlobalHook.objects.create(name="global-hook4",
                                                      model="Instance",
                                                      state=InstanceState.AVAILABLE,
                                                      job_template=self.job_template_test,
                                                      extra_vars={"key4": "value4"})

    def test_filter_by_instance_state(self):
        data = {
            'state_instance': [InstanceState.AVAILABLE],
        }
        hook_filter = GlobalHookFilter(data)
        self.assertTrue(hook_filter.form.is_valid())
        self.assertEquals(1, hook_filter.qs.count())
        self.assertEquals(self.global_hook4, hook_filter.qs[0])

    def test_filter_by_request_state(self):
        data = {
            'state_request': [RequestState.REJECTED]
        }
        hook_filter = GlobalHookFilter(data)
        self.assertTrue(hook_filter.form.is_valid())
        self.assertEquals(1, hook_filter.qs.count())
        self.assertEquals(self.global_hook3, hook_filter.qs[0])

    def test_filter_by_instance_and_request_state(self):
        data = {
            'state_instance': [InstanceState.AVAILABLE],
            'state_request': [RequestState.REJECTED]
        }
        hook_filter = GlobalHookFilter(data)
        self.assertTrue(hook_filter.form.is_valid())
        self.assertEquals(2, hook_filter.qs.count())
        self.assertIn(self.global_hook4, hook_filter.qs)
        self.assertIn(self.global_hook3, hook_filter.qs)
