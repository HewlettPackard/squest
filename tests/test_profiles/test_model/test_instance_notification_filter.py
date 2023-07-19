from service_catalog.models import InstanceState
from tests.test_profiles.base.base_test_support_notification_filter import BaseTestInstanceNotification


class TestInstanceNotificationFilter(BaseTestInstanceNotification):

    def setUp(self):
        super(TestInstanceNotificationFilter, self).setUp()

    def test_when_render(self):
        # test with 2 existing key and correct values
        self.support_notification_filter_test.when = "instance.spec['spec_key1'] == 'spec_value1' and " \
                                                      "instance.user_spec['user_spec_key1'] == 'user_spec_value1'"
        self.support_notification_filter_test.save()
        self.assertTrue(self.support_notification_filter_test.when_render(self.test_instance))

        # test with 2 existing key and 1 correct values
        self.support_notification_filter_test.when = "instance.spec['spec_key1'] == 'not_target_val' and " \
                                                      "instance.user_spec['user_spec_key1'] == 'user_spec_value1'"
        self.support_notification_filter_test.save()
        self.assertFalse(self.support_notification_filter_test.when_render(self.test_instance))

        # test with on non existing key
        self.support_notification_filter_test.when = "instance.spec['non_exist'] == 'spec_value1' and " \
                                                      "instance.user_spec['user_spec_key1'] == 'user_spec_value1'"
        self.support_notification_filter_test.save()
        self.assertFalse(self.support_notification_filter_test.when_render(self.test_instance))

        # test with on non-existing key but OR condition
        self.support_notification_filter_test.when = "instance.spec['non_exist'] == 'spec_value1' or " \
                                                      "instance.user_spec['user_spec_key1'] == 'user_spec_value1'"
        self.support_notification_filter_test.save()
        self.assertTrue(self.support_notification_filter_test.when_render(self.test_instance))

        # test with on non-existing context (user spec or spec)
        self.support_notification_filter_test.when = "non_exist_context['my_key'] == 'spec_value1'"
        self.support_notification_filter_test.save()
        self.assertFalse(self.support_notification_filter_test.when_render(self.test_instance))

        # test with an instance field
        self.support_notification_filter_test.when = "instance.name == 'test_instance_3'"
        self.support_notification_filter_test.save()
        self.assertTrue(self.support_notification_filter_test.when_render(self.test_instance_3))

    def test_is_authorized_without_criteria_set(self):
        self.assertTrue(self.support_notification_filter_test.is_authorized(instance=None))
        self.assertTrue(self.support_notification_filter_test.is_authorized(instance=self.test_instance))
        self.assertTrue(self.support_notification_filter_test.is_authorized(instance=self.test_instance_2))
        self.assertTrue(self.support_notification_filter_test.is_authorized(instance=self.test_instance_3))

    def test_is_authorized_with_one_service(self):
        self.support_notification_filter_test.services.add(self.service_test)
        self.support_notification_filter_test.save()
        self.assertTrue(self.support_notification_filter_test.is_authorized(instance=self.test_instance))
        self.assertFalse(self.support_notification_filter_test.is_authorized(instance=self.test_instance_3))

    def test_is_authorized_with_two_service(self):
        self.support_notification_filter_test.services.add(self.service_test, self.service_test_2)
        self.support_notification_filter_test.save()
        self.assertTrue(self.support_notification_filter_test.is_authorized(instance=self.test_instance))
        self.assertTrue(self.support_notification_filter_test.is_authorized(instance=self.test_instance_2))
        self.assertFalse(self.support_notification_filter_test.is_authorized(instance=self.test_instance_3))

    def test_is_authorized_with_one_instance_state(self):
        self.test_instance.state = InstanceState.AVAILABLE
        self.test_instance.save()
        self.test_instance_2.state = InstanceState.PENDING
        self.test_instance_2.save()
        self.support_notification_filter_test.instance_states = [InstanceState.AVAILABLE]
        self.support_notification_filter_test.save()
        self.assertTrue(self.support_notification_filter_test.is_authorized(instance=self.test_instance))
        self.assertFalse(self.support_notification_filter_test.is_authorized(instance=self.test_instance_2))
        self.assertFalse(self.support_notification_filter_test.is_authorized(instance=self.test_instance_3))

    def test_is_authorized_with_two_request_state(self):
        self.test_instance_3.state = InstanceState.ARCHIVED
        self.test_instance_3.save()
        self.support_notification_filter_test.instance_states = [InstanceState.AVAILABLE, InstanceState.PENDING]
        self.support_notification_filter_test.save()
        self.assertTrue(self.support_notification_filter_test.is_authorized(instance=self.test_instance))
        self.assertTrue(self.support_notification_filter_test.is_authorized(instance=self.test_instance_2))
        self.assertFalse(self.support_notification_filter_test.is_authorized(instance=self.test_instance_3))

    def test_is_authorized_with_when(self):
        self.support_notification_filter_test.when = "instance.spec['spec_key1'] == 'spec_value1' and " \
                                                      "instance.user_spec['user_spec_key1'] == 'user_spec_value1'"
        self.support_notification_filter_test.save()
        self.assertTrue(self.support_notification_filter_test.is_authorized(instance=self.test_instance))
        self.assertFalse(self.support_notification_filter_test.is_authorized(instance=self.test_instance_2))

    def test_is_authorized_with_all_filter(self):
        self.support_notification_filter_test.services.add(self.service_test)
        self.support_notification_filter_test.instance_states = [InstanceState.PENDING]
        self.support_notification_filter_test.when = "instance.spec['spec_key1'] == 'spec_value1' and " \
                                                      "instance.user_spec['user_spec_key1'] == 'user_spec_value1'"
        self.support_notification_filter_test.save()
        self.assertTrue(
            self.support_notification_filter_test.is_authorized(instance=self.test_instance))
        self.assertFalse(
            self.support_notification_filter_test.is_authorized(instance=self.test_instance_3))
