from django.test import TestCase
from rest_framework.test import APITestCase

from service_catalog.models import Operation, OperationType
from tests.setup import SetupServiceCommon


class SetupOperationCommon(SetupServiceCommon):

    def setUp(self):
        super().setUp()
        # Create operation
        self.operation_create_1 = Operation.objects.create(
            name="Operation 1 (Create)",
            service=self.service_1,
            job_template=self.job_template_1,
            process_timeout_second=30
        )

        self.operation_create_2 = Operation.objects.create(
            name="Operation 2 (Create)",
            service=self.service_2,
            job_template=self.job_template_1,
            process_timeout_second=30
        )
        self.operation_update_1 = Operation.objects.create(
            name="Operation 3 (Update)",
            type=OperationType.UPDATE,
            service=self.service_2,
            job_template=self.job_template_1,
            process_timeout_second=30
        )
        print("SetupOperationCommon finished")


class SetupOperation(TestCase, SetupOperationCommon):
    pass


class SetupOperationAPI(APITestCase, SetupOperationCommon):
    pass
