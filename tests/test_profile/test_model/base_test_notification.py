from service_catalog.models import Request, RequestState, Instance, Service, Operation
from tests.test_profile.base_test_profile import BaseTestProfile


class BaseTestNotificationFilter(BaseTestProfile):

    def setUp(self):
        super(BaseTestNotificationFilter, self).setUp()
        self.service_test_3 = Service.objects.create(name="service-test-3", description="description-of-service-test-3")
        self.create_operation_test_3 = Operation.objects.create(name="create test",
                                                                service=self.service_test_3,
                                                                job_template=self.job_template_test)
        self.test_instance_3 = Instance.objects.create(name="test_instance_3",
                                                       service=self.service_test_3,
                                                       spoc=self.standard_user_2)
        self.test_request_3 = Request.objects.create(fill_in_survey={"location": "grenoble"},
                                                     instance=self.test_instance_3,
                                                     operation=self.create_operation_test_3,
                                                     user=self.standard_user,
                                                     state=RequestState.ARCHIVED)
