import sys

from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestTowerSurveyField(BaseTestRequest):

    def test_fill_in_survey_updated(self):
        admin_fill_in_survey = {
            'multiplechoice_variable': "choice1",
            'multiselect_var': [],
            'textarea_var': "textarea_value",
            'password_var': "password_val",
            'float_var': 0,
            'integer_var': 12
        }
        fill_in_survey = {
            'text_variable': "value"
        }

        self.test_request.fill_in_survey = fill_in_survey
        self.test_request.admin_fill_in_survey = admin_fill_in_survey
        self.test_request.save()

        expected_admin_fill_in_survey = {
            'text_variable': "value",
            'multiplechoice_variable': "choice1",
            'multiselect_var': [],
            'password_var': "password_val",
            'float_var': 0,
            'integer_var': 12
        }
        expected_fill_in_survey = {
            'textarea_var': "textarea_value",
        }

        new_survey_config = {
            'text_variable': False,
            'multiplechoice_variable': False,
            'multiselect_var': False,
            'textarea_var': True,
            'password_var': False,
            'float_var': False,
            'integer_var': False
        }
        self.test_request.operation.switch_tower_fields_enable_from_dict(new_survey_config)
        self.test_request.refresh_from_db()
        self.assertDictEqual(self.test_request.fill_in_survey, expected_fill_in_survey)
        self.assertDictEqual(self.test_request.admin_fill_in_survey, expected_admin_fill_in_survey)

    def test_get_maximum_value(self):
        test_case_list = [
            {"quota": 50, "survey": 30, "expected": 30},
            {"quota": '50', "survey": '30', "expected": 30},
            {"quota": 30, "survey": 50, "expected": 30},
            {"quota": None, "survey": 50, "expected": 50},
            {"quota": 50, "survey": None, "expected": 50},
            {"quota": None, "survey": None, "expected": sys.maxsize},
        ]
        survey_field = self.create_operation_test.tower_survey_fields.first()
        for test_case in test_case_list:
            self.assertEqual(survey_field.get_maximum_value(test_case.get("quota"), test_case.get("survey")), test_case.get("expected"))
