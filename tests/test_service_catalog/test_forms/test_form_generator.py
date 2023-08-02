from service_catalog.forms import FormGenerator
from service_catalog.models import TowerSurveyField
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestFormGenerator(BaseTestRequest):

    def setUp(self):
        super(TestFormGenerator, self).setUp()

    def test_apply_jinja_template_to_survey_empty_default(self):

        self.test_request.operation.job_template.survey = {
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
        self.test_request.operation.job_template.save()

        # test with en empty string
        target_field = TowerSurveyField.objects.get(name="text_variable", operation=self.create_operation_test)
        target_field.default = ""
        target_field.save()
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
        form_generator = FormGenerator(squest_request=self.test_request)
        form_generator._apply_jinja_template_to_survey()
        self.assertDictEqual(expected_result,
                             form_generator.survey_as_dict)

    def test_apply_jinja_template_to_survey_override_default(self):
        self.test_request.operation.job_template.survey = {
            "name": "test-survey",
            "description": "test-survey-description",
            "spec": [
                {
                    "choices": "",
                    "default": "this_was_the_default",
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
        self.test_request.operation.job_template.save()
        # test with en empty string
        target_field = TowerSurveyField.objects.get(name="text_variable", operation=self.create_operation_test)
        target_field.default = "this_is_the_new_default"
        target_field.save()
        expected_result = {
            "name": "test-survey",
            "description": "test-survey-description",
            "spec": [
                {
                    "choices": "",
                    "default": "this_is_the_new_default",
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
        form_generator = FormGenerator(squest_request=self.test_request)
        form_generator._apply_jinja_template_to_survey()
        self.assertDictEqual(expected_result,
                             form_generator.survey_as_dict)

    def test_apply_jinja_template_to_survey_with_spec_variable(self):
        self.test_request.operation.job_template.survey = {
            "name": "test-survey",
            "description": "test-survey-description",
            "spec": [
                {
                    "choices": "",
                    "default": "this_was_the_default",
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
        self.job_template_test.save()
        # test with jinja string
        target_field = TowerSurveyField.objects.get(name="text_variable", operation=self.create_operation_test)
        target_field.default = "{{ instance.spec.os }}"
        target_field.save()
        self.test_instance.spec = {
            "os": "linux"
        }
        self.test_instance.save()
        expected_result = {
            "name": "test-survey",
            "description": "test-survey-description",
            "spec": [
                {
                    "choices": "",
                    "default": "linux",
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
        form_generator = FormGenerator(squest_request=self.test_request, squest_instance=self.test_instance)
        form_generator._apply_jinja_template_to_survey()
        self.assertDictEqual(expected_result,
                             form_generator.survey_as_dict)

    def test_apply_user_validator_to_survey(self):
        self.job_template_test.survey = {
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
        self.job_template_test.save()
        # test with en empty string
        target_field = TowerSurveyField.objects.get(name="text_variable", operation=self.create_operation_test)
        target_field.validators = "even_number,superior_to_10"
        target_field.save()
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
                    "variable": "text_variable",
                    "validators": ["even_number", "superior_to_10"]
                }
            ],
        }
        self.maxDiff = None
        form_generator = FormGenerator(squest_request=self.test_request, squest_instance=self.test_instance)
        form_generator._apply_user_validator_to_survey()
        self.assertDictEqual(expected_result,
                             form_generator.survey_as_dict)

    def test_get_customer_field_only(self):
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
        form_generator = FormGenerator(operation=self.create_operation_test)
        form_generator._get_customer_field_only()
        self.assertDictEqual(expected_result,
                             form_generator.survey_as_dict)
