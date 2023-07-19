from service_catalog.models import  RequestState
from tests.test_profiles.base.base_test_request_notification_filter import BaseTestRequestNotification


class TestRequestNotificationFilter(BaseTestRequestNotification):

    def setUp(self):
        super(TestRequestNotificationFilter, self).setUp()
        self.test_request_3.fill_in_survey = {"location": "grenoble"}
        self.test_request_3.save()

    def test_when_render(self):
        # test with 2 existing key and correct values
        self.request_notification_filter_test.when = "request.instance.spec['spec_key1'] == 'spec_value1' and " \
                                                     "request.instance.user_spec['user_spec_key1'] == 'user_spec_value1'"
        self.request_notification_filter_test.save()
        self.assertTrue(self.request_notification_filter_test.when_render(self.test_request))

        # test with 2 existing key and 1 correct values
        self.request_notification_filter_test.when = "request.instance.spec['spec_key1'] == 'not_target_val' and " \
                                                     "request.instance.user_spec['user_spec_key1'] == 'user_spec_value1'"
        self.request_notification_filter_test.save()
        self.assertFalse(self.request_notification_filter_test.when_render(self.test_request))

        # test with on non existing key
        self.request_notification_filter_test.when = "request.instance.spec['non_exist'] == 'spec_value1' and " \
                                                     "request.instance.user_spec['user_spec_key1'] == 'user_spec_value1'"
        self.request_notification_filter_test.save()
        self.assertFalse(self.request_notification_filter_test.when_render(self.test_request))

        # test with on non existing key but OR condition
        self.request_notification_filter_test.when = "request.instance.spec['non_exist'] == 'spec_value1' or " \
                                                     "request.instance.user_spec['user_spec_key1'] == 'user_spec_value1'"
        self.request_notification_filter_test.save()
        self.assertTrue(self.request_notification_filter_test.when_render(self.test_request))

        # test with on non existing context (user spec or spec)
        self.request_notification_filter_test.when = "non_exist_context['my_key'] == 'spec_value1'"
        self.request_notification_filter_test.save()
        self.assertFalse(self.request_notification_filter_test.when_render(self.test_request))

        # test with a fill_in_survey field
        self.request_notification_filter_test.when = "request.fill_in_survey['location'] == 'grenoble'"
        self.request_notification_filter_test.save()
        self.assertTrue(self.request_notification_filter_test.when_render(self.test_request_3))

    def test_is_authorized_without_criteria_set(self):
        self.assertTrue(self.request_notification_filter_test.is_authorized(request=None))
        self.assertTrue(self.request_notification_filter_test.is_authorized(request=self.test_request))
        self.assertTrue(self.request_notification_filter_test.is_authorized(request=self.test_request_2))
        self.assertTrue(self.request_notification_filter_test.is_authorized(request=self.test_request_3))

    def test_is_authorized_with_one_service(self):
        self.request_notification_filter_test.services.add(self.service_test)
        self.request_notification_filter_test.save()
        self.assertTrue(self.request_notification_filter_test.is_authorized(request=self.test_request))
        self.assertFalse(self.request_notification_filter_test.is_authorized(request=self.test_request_3))

    def test_is_authorized_with_one_operation(self):
        self.request_notification_filter_test.operations.add(self.create_operation_test)
        self.request_notification_filter_test.save()
        self.assertTrue(self.request_notification_filter_test.is_authorized(request=self.test_request))
        self.assertFalse(self.request_notification_filter_test.is_authorized(request=self.test_request_2))

    def test_is_authorized_with_one_request_state(self):
        self.request_notification_filter_test.request_states = [RequestState.SUBMITTED]
        self.request_notification_filter_test.save()
        self.assertTrue(self.request_notification_filter_test.is_authorized(request=self.test_request))
        self.assertFalse(self.request_notification_filter_test.is_authorized(request=self.test_request_2))

    def test_is_authorized_with_one_when(self):
        self.request_notification_filter_test.when = "request.instance.spec['spec_key1'] == 'spec_value1' and request.instance.user_spec['user_spec_key1'] == 'user_spec_value1'"
        self.request_notification_filter_test.save()
        self.assertTrue(self.request_notification_filter_test.is_authorized(request=self.test_request))
        self.assertFalse(self.request_notification_filter_test.is_authorized(request=self.test_request_2))

    def test_is_authorized_with_two_service(self):
        self.request_notification_filter_test.services.add(self.service_test, self.service_test_2)
        self.request_notification_filter_test.save()
        self.assertTrue(self.request_notification_filter_test.is_authorized(request=self.test_request))
        self.assertTrue(self.request_notification_filter_test.is_authorized(request=self.test_request_2))
        self.assertFalse(self.request_notification_filter_test.is_authorized(request=self.test_request_3))

    def test_is_authorized_with_two_operation(self):
        self.request_notification_filter_test.operations.add(self.update_operation_test, self.create_operation_test)
        self.request_notification_filter_test.save()
        self.assertTrue(self.request_notification_filter_test.is_authorized(request=self.test_request))
        self.assertTrue(self.request_notification_filter_test.is_authorized(request=self.test_request_2))
        self.assertFalse(self.request_notification_filter_test.is_authorized(request=self.test_request_3))

    def test_is_authorized_with_two_request_state(self):
        self.request_notification_filter_test.request_states = [RequestState.SUBMITTED, RequestState.ACCEPTED]
        self.request_notification_filter_test.save()
        self.assertTrue(self.request_notification_filter_test.is_authorized(request=self.test_request))
        self.assertTrue(self.request_notification_filter_test.is_authorized(request=self.test_request_2))
        self.assertFalse(self.request_notification_filter_test.is_authorized(request=self.test_request_3))

    def test_is_authorized_with_a_service_and_operation_in_same_service(self):
        self.request_notification_filter_test.services.add(self.service_test)
        self.request_notification_filter_test.operations.add(self.create_operation_test)
        self.request_notification_filter_test.save()
        self.assertTrue(self.request_notification_filter_test.is_authorized(request=self.test_request))
        self.assertFalse(self.request_notification_filter_test.is_authorized(request=self.test_request_3))

    def test_is_authorized_with_a_service_and_operation_in_another_service(self):
        self.request_notification_filter_test.services.add(self.service_test)
        self.request_notification_filter_test.operations.add(self.delete_operation_test_2)
        self.request_notification_filter_test.save()
        self.assertFalse(
            self.request_notification_filter_test.is_authorized(request=self.test_request))

    def test_is_authorized_with_all_filter(self):
        self.request_notification_filter_test.services.add(self.service_test)
        self.request_notification_filter_test.operations.add(self.create_operation_test)
        self.request_notification_filter_test.request_states = [RequestState.SUBMITTED]
        self.request_notification_filter_test.when = "request.instance.spec['spec_key1'] == 'spec_value1' and request.instance.user_spec['user_spec_key1'] == 'user_spec_value1'"
        self.request_notification_filter_test.save()
        self.assertTrue(
            self.request_notification_filter_test.is_authorized(request=self.test_request))
        self.assertFalse(
            self.request_notification_filter_test.is_authorized(request=self.test_request_3))
