from django.urls import reverse

from service_catalog.forms import ServiceRequestForm
from tests.base import BaseTest


class BaseTestRequest(BaseTest):

    def setUp(self):
        super(BaseTestRequest, self).setUp()
        form_data = {'instance_name': 'test instance', 'text_variable': 'my_var'}
        form = ServiceRequestForm(user=self.standard_user,
                                  service_id=self.service_test.id,
                                  data=form_data)
        form.is_valid()
        self.test_request = form.save()
