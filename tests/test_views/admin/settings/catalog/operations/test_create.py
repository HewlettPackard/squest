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

    def test_create_a_delete_service_operation(self):
        data = {
            "name": "new_service",
            "description": "a new service",
            "job_template": self.job_template_test.id,
            "type": "DELETE",
            "process_timeout_second": 60
        }
        number_operation_before = Operation.objects.filter(service=self.service_test.id).count()
        response = self.client.post(self.url, data=data)
        self.assertEquals(302, response.status_code)
        self.assertEquals(number_operation_before + 1,
                          Operation.objects.filter(service=self.service_test.id).count())

    def test_create_an_update_service_operation(self):
        data = {
            "name": "new_service",
            "description": "a new service",
            "job_template": self.job_template_test.id,
            "type": "UPDATE",
            "process_timeout_second": 60
        }
        number_operation_before = Operation.objects.filter(service=self.service_test.id).count()
        response = self.client.post(self.url, data=data)
        self.assertEquals(302, response.status_code)
        self.assertEquals(number_operation_before + 1,
                          Operation.objects.filter(service=self.service_test.id).count())

    def test_create_a_create_service_operation(self):
        """
        Only one create operation per service, it will fail
        """
        data = {
            "name": "new_service",
            "description": "a new service",
            "job_template": self.job_template_test.id,
            "type": "CREATE",
            "process_timeout_second": 60
        }
        number_operation_before = Operation.objects.filter(service=self.service_test.id).count()
        response = self.client.post(self.url, data=data)
        self.assertEquals(200, response.status_code)
        self.assertEquals(number_operation_before,
                          Operation.objects.filter(service=self.service_test.id).count())

    def test_cannot_add_service_operation_when_logout(self):
        self.client.logout()
        data = {
            "name": "new_service",
            "description": "a new service",
            "job_template": self.job_template_test.id,
            "type": "CREATE",
            "process_timeout_second": 60
        }
        response = self.client.post(self.url, data=data)
        self.assertEquals(302, response.status_code)
