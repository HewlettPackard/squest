from service_catalog.models import Operation
from tests.test_service_catalog.base import BaseTest


class TestOperation(BaseTest):

    def setUp(self):
        super(TestOperation, self).setUp()

    def test_survey_from_job_template_is_copied_on_create(self):
        new_operation = Operation.objects.create(name="new test",
                                                 service=self.service_test,
                                                 job_template=self.job_template_test,
                                                 process_timeout_second=20)
        for field in self.job_template_test.survey["spec"]:
            self.assertTrue(new_operation.tower_survey_fields.filter(variable=field["variable"], is_customer_field=True).exists())

    def test_service_is_disabled_when_the_create_operation_disabled(self):
        self.assertTrue(self.create_operation_test.service.enabled)
        self.assertTrue(self.create_operation_test.enabled)
        self.create_operation_test.enabled = False
        self.create_operation_test.save()
        self.assertFalse(self.create_operation_test.service.enabled)
        self.assertFalse(self.create_operation_test.enabled)
