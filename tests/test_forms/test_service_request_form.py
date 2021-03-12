from service_catalog.forms import ServiceRequestForm
from tests.base import BaseTest


class TestServiceRequestForm(BaseTest):

    def setUp(self):
        super(TestServiceRequestForm, self).setUp()

    def test_get_available_fields(self):
        expected_result = {
            "name": "test-survey",
            "description": "test-survey-description",
            "spec": [
                {
                    "choices": "",
                    "default": "",
                    "max": 1024,
                    "min": 0,
                    "new_question": True,
                    "question_description": "",
                    "question_name": "String variable",
                    "required": True,
                    "type": "text",
                    "variable": "text_variable"
                }
            ]
        }

        self.assertEquals(expected_result,
                          ServiceRequestForm._get_available_fields(job_template_survey=self.job_template_test.survey,
                                                                   operation_survey=self.create_operation_test.survey))
