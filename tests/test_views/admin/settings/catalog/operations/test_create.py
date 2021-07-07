from django.urls import reverse

from service_catalog.models import Operation
from tests.base import BaseTest


class OperationCreateTestCase(BaseTest):

    def setUp(self):
        super(OperationCreateTestCase, self).setUp()
        args = {
            'service_id': self.service_test.id,
        }
        self.url = reverse('service_catalog:add_service_operation', kwargs=args)

    def test_create_service_operation(self):
        data = {
            "name": "new_service",
            "description": "a new service",
            "job_template": self.job_template_test.name,
            "type": "DELETE",
            "process_timeout_second": 60
        }
        number_operation_before = Operation.objects.filter(service=self.service_test.id).count()
        response = self.client.post(self.url, data=data)
        self.assertEquals(302, response.status_code)
        self.assertEquals(number_operation_before + 1,
                          Operation.objects.filter(service=self.service_test.id).count())
