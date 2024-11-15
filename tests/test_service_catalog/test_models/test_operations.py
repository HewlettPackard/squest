from copy import deepcopy

from service_catalog.models import Operation, OperationType
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestOperation(BaseTestRequest):

    def assertSurveyIsValid(self):
        self.job_template_test.refresh_from_db()
        position = 0
        for field in self.job_template_test.survey["spec"]:
            self.assertTrue(
                self.new_operation.tower_survey_fields.filter(variable=field["variable"],
                                                              is_customer_field=True, position=position).exists())
            position += 1
        self.assertEqual(len(self.job_template_test.survey["spec"]), self.new_operation.tower_survey_fields.count())

    def setUp(self):
        super(TestOperation, self).setUp()
        self.new_operation = Operation.objects.create(name="new test",
                                                      type=OperationType.UPDATE,
                                                      service=self.service_test,
                                                      job_template=self.job_template_test,
                                                      process_timeout_second=20)

    def test_survey_from_job_template_is_copied_on_create(self):
        self.assertSurveyIsValid()

    def test_service_is_disabled_when_the_create_operation_disabled(self):
        self.assertTrue(self.create_operation_test.service.enabled)
        self.assertTrue(self.create_operation_test.enabled)
        self.create_operation_test.enabled = False
        self.create_operation_test.save()
        self.assertFalse(self.create_operation_test.service.enabled)
        self.assertFalse(self.create_operation_test.enabled)

    def test_update_survey_when_position_is_default(self):
        self.new_operation.tower_survey_fields.update(position=0)
        self.assertFalse(self.new_operation.tower_survey_fields.exclude(position=0).exists())
        self.new_operation.update_survey()
        self.assertSurveyIsValid()

    def test_update_survey_when_field_is_removed_from_awx(self):
        previous_count = len(self.job_template_test.survey["spec"])
        self.job_template_test.survey["spec"].pop(1)
        self.job_template_test.save()
        current_count = len(self.job_template_test.survey["spec"])
        self.assertEqual(previous_count - 1, current_count)
        self.new_operation.update_survey()
        self.assertSurveyIsValid()

    def test_update_survey_when_field_is_added_from_awx(self):
        previous_count = len(self.job_template_test.survey["spec"])
        tmp = deepcopy(self.job_template_test.survey["spec"][1])
        self.job_template_test.survey["spec"][1]["variable"] = "test_swapped"
        self.job_template_test.survey["spec"].append(tmp)
        self.job_template_test.save()
        current_count = len(self.job_template_test.survey["spec"])
        self.assertEqual(previous_count + 1, current_count)
        self.new_operation.update_survey()
        self.assertSurveyIsValid()

    def test_when_instance_authorized(self):
        self.test_instance.user_spec = {
            "location": "chambery"
        }
        self.test_instance.save()
        # by default when no condition set we always return true
        self.assertTrue(self.update_operation_test.when_instance_authorized(self.test_instance))

        # set a condition
        self.update_operation_test.when = "instance.user_spec.location=='grenoble'"
        self.update_operation_test.save()
        self.assertFalse(self.update_operation_test.when_instance_authorized(self.test_instance))

        # update the instance spec to match the condition
        self.test_instance.user_spec = {
            "location": "grenoble"
        }
        self.test_instance.save()
        self.assertTrue(self.update_operation_test.when_instance_authorized(self.test_instance))
