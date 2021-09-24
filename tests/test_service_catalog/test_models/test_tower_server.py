from unittest.mock import patch, MagicMock

from service_catalog.models import JobTemplate, Operation
from tests.test_service_catalog.base import BaseTest


class TestTowerServer(BaseTest):

    def setUp(self):
        super(TestTowerServer, self).setUp()

    @patch('service_catalog.models.tower_server.TowerServer.get_tower_instance')
    def test_sync_same_survey(self, mock_tower_instance):
        # test sync with same job template
        mock_tower_instance.return_value = MagicMock(
            job_templates=[
                MagicMock(
                    id=1,
                    survey_spec=self.testing_survey,
                    _data=self.job_template_testing_data
                )
            ]
        )
        mock_tower_instance.return_value.job_templates[0].name = "Mock"
        self.tower_server_test.sync()
        mock_tower_instance.assert_called()
        # assert that the survey is the same
        self.assertDictEqual(self.testing_survey, self.job_template_test.survey)

    @patch('service_catalog.models.tower_server.TowerServer.get_tower_instance')
    def test_sync_survey_changed(self, mock_tower_instance):
        # test sync with a new job template
        new_survey = {
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
                    "question_name": "Updated variable",
                    "required": True,
                    "type": "text",
                    "variable": "updated_text_variable"
                },
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
                },
            ]
        }
        mock_tower_instance.return_value = MagicMock(
            job_templates=[
                MagicMock(
                    id=1,
                    survey_spec=new_survey,
                    _data=self.job_template_testing_data
                )
            ]
        )
        mock_tower_instance.return_value.job_templates[0].name = "Mock"
        self.tower_server_test.sync()
        # assert that the survey has been updated
        updated_template = JobTemplate.objects.get(id=self.job_template_test.id,
                                                   tower_server=self.tower_server_test)
        self.assertDictEqual(new_survey, updated_template.survey)
        # check that the operation enabled_survey_fields has been updated
        expected_dict = {
            'updated_text_variable': True,
            'text_variable': True
        }
        updated_operation = Operation.objects.get(id=self.create_operation_test.id)
        self.assertDictEqual(expected_dict, updated_operation.enabled_survey_fields)
