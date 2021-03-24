from service_catalog.models import Request, Instance
from tests.base import BaseTest


class BaseTestRequest(BaseTest):

    def setUp(self):
        super(BaseTestRequest, self).setUp()
        form_data = {'instance_name': 'test instance', 'text_variable': 'my_var'}
        self.test_instance = Instance.objects.create(name="test_instance_1", service=self.service_test)
        self.test_request = Request.objects.create(fill_in_survey=form_data,
                                                   instance=self.test_instance,
                                                   operation=self.create_operation_test,
                                                   user=self.standard_user)
