from service_catalog.models import Request, RequestState, Instance, Service, Operation
from tests.test_profile.base_test_profile import BaseTestProfile


class TestNotificationFilter(BaseTestProfile):

    def setUp(self):
        super(TestNotificationFilter, self).setUp()
        self.service_test_3 = Service.objects.create(name="service-test-3", description="description-of-service-test-3")
        self.create_operation_test_3 = Operation.objects.create(name="create test",
                                                                service=self.service_test_3,
                                                                job_template=self.job_template_test)
        self.test_instance_3 = Instance.objects.create(name="test_instance_2",
                                                       service=self.service_test_3,
                                                       spoc=self.standard_user_2)
        self.test_request_3 = Request.objects.create(fill_in_survey={"location": "grenoble"},
                                                     instance=self.test_instance_3,
                                                     operation=self.create_operation_test_3,
                                                     user=self.standard_user,
                                                     state=RequestState.ARCHIVED)

    def test_when_render(self):
        # test with 2 existing key and correct values
        self.notification_filter_test.when = "request.instance.spec['spec_key1'] == 'spec_value1' and request.instance.user_spec['user_spec_key1'] == 'user_spec_value1'"
        self.notification_filter_test.save()
        self.assertTrue(self.notification_filter_test.when_render(self.test_request))

        # test with 2 existing key and 1 correct values
        self.notification_filter_test.when = "request.instance.spec['spec_key1'] == 'not_target_val' and request.instance.user_spec['user_spec_key1'] == 'user_spec_value1'"
        self.notification_filter_test.save()
        self.assertFalse(self.notification_filter_test.when_render(self.test_request))

        # test with on non existing key
        self.notification_filter_test.when = "request.instance.spec['non_exist'] == 'spec_value1' and request.instance.user_spec['user_spec_key1'] == 'user_spec_value1'"
        self.notification_filter_test.save()
        self.assertFalse(self.notification_filter_test.when_render(self.test_request))

        # test with on non existing key but OR condition
        self.notification_filter_test.when = "request.instance.spec['non_exist'] == 'spec_value1' or request.instance.user_spec['user_spec_key1'] == 'user_spec_value1'"
        self.notification_filter_test.save()
        self.assertTrue(self.notification_filter_test.when_render(self.test_request))

        # test with on non existing context (user spec or spec)
        self.notification_filter_test.when = "non_exist_context['my_key'] == 'spec_value1'"
        self.notification_filter_test.save()
        self.assertFalse(self.notification_filter_test.when_render(self.test_request))

        # test with a fill_in_survey field
        self.notification_filter_test.when = "request.fill_in_survey['location'] == 'grenoble'"
        self.notification_filter_test.save()
        self.assertTrue(self.notification_filter_test.when_render(self.test_request_3))

    def test_is_authorized_without_criteria_set(self):
        self.assertTrue(self.notification_filter_test.is_authorized(request=None))
        self.assertTrue(self.notification_filter_test.is_authorized(request=self.test_request))
        self.assertTrue(self.notification_filter_test.is_authorized(request=self.test_request_2))
        self.assertTrue(self.notification_filter_test.is_authorized(request=self.test_request_3))

    def test_is_authorized_with_one_service(self):
        self.notification_filter_test.services.add(self.service_test)
        self.notification_filter_test.save()
        self.assertTrue(self.notification_filter_test.is_authorized(request=self.test_request))
        self.assertFalse(self.notification_filter_test.is_authorized(request=self.test_request_3))

    def test_is_authorized_with_one_operation(self):
        self.notification_filter_test.operations.add(self.create_operation_test)
        self.notification_filter_test.save()
        self.assertTrue(self.notification_filter_test.is_authorized(request=self.test_request))
        self.assertFalse(self.notification_filter_test.is_authorized(request=self.test_request_2))

    def test_is_authorized_with_one_request_state(self):
        self.notification_filter_test.request_states = [RequestState.SUBMITTED]
        self.notification_filter_test.save()
        self.assertTrue(self.notification_filter_test.is_authorized(request=self.test_request))
        self.assertFalse(self.notification_filter_test.is_authorized(request=self.test_request_2))

    def test_is_authorized_with_one_when(self):
        self.notification_filter_test.when = "request.instance.spec['spec_key1'] == 'spec_value1' and request.instance.user_spec['user_spec_key1'] == 'user_spec_value1'"
        self.notification_filter_test.save()
        self.assertTrue(self.notification_filter_test.is_authorized(request=self.test_request))
        self.assertFalse(self.notification_filter_test.is_authorized(request=self.test_request_2))

    def test_is_authorized_with_two_service(self):
        self.notification_filter_test.services.add(self.service_test, self.service_test_2)
        self.notification_filter_test.save()
        self.assertTrue(self.notification_filter_test.is_authorized(request=self.test_request))
        self.assertTrue(self.notification_filter_test.is_authorized(request=self.test_request_2))
        self.assertFalse(self.notification_filter_test.is_authorized(request=self.test_request_3))

    def test_is_authorized_with_two_operation(self):
        self.notification_filter_test.operations.add(self.update_operation_test, self.create_operation_test)
        self.notification_filter_test.save()
        self.assertTrue(self.notification_filter_test.is_authorized(request=self.test_request))
        self.assertTrue(self.notification_filter_test.is_authorized(request=self.test_request_2))
        self.assertFalse(self.notification_filter_test.is_authorized(request=self.test_request_3))

    def test_is_authorized_with_two_request_state(self):
        self.notification_filter_test.request_states = [RequestState.SUBMITTED, RequestState.ACCEPTED]
        self.notification_filter_test.save()
        self.assertTrue(self.notification_filter_test.is_authorized(request=self.test_request))
        self.assertTrue(self.notification_filter_test.is_authorized(request=self.test_request_2))
        self.assertFalse(self.notification_filter_test.is_authorized(request=self.test_request_3))

    def test_is_authorized_with_a_service_and_operation_in_same_service(self):
        self.notification_filter_test.services.add(self.service_test)
        self.notification_filter_test.operations.add(self.create_operation_test)
        self.notification_filter_test.save()
        self.assertTrue(self.notification_filter_test.is_authorized(request=self.test_request))
        self.assertFalse(self.notification_filter_test.is_authorized(request=self.test_request_3))

    def test_is_authorized_with_a_service_and_operation_in_another_service(self):
        self.notification_filter_test.services.add(self.service_test)
        self.notification_filter_test.operations.add(self.delete_operation_test_2)
        self.notification_filter_test.save()
        self.assertFalse(
            self.notification_filter_test.is_authorized(request=self.test_request))

    def test_is_authorized_with_all_filter(self):
        self.notification_filter_test.services.add(self.service_test)
        self.notification_filter_test.operations.add(self.create_operation_test)
        self.notification_filter_test.request_states = [RequestState.SUBMITTED]
        self.notification_filter_test.when = "request.instance.spec['spec_key1'] == 'spec_value1' and request.instance.user_spec['user_spec_key1'] == 'user_spec_value1'"
        self.notification_filter_test.save()
        self.assertTrue(
            self.notification_filter_test.is_authorized(request=self.test_request))
        self.assertFalse(
            self.notification_filter_test.is_authorized(request=self.test_request_3))
