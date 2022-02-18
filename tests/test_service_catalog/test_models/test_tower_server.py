from unittest.mock import patch, MagicMock

from service_catalog.models import JobTemplate, Operation
from tests.test_service_catalog.base import BaseTest


class TestTowerServer(BaseTest):

    def setUp(self):
        super(TestTowerServer, self).setUp()

        self.new_survey = {
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

    def test_str(self):
        self.assertEqual("tower-server-test (localhost)", str(self.tower_server_test))

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
        mock_tower_instance.return_value = MagicMock(
            job_templates=[
                MagicMock(
                    id=1,
                    survey_spec=self.new_survey,
                    _data=self.job_template_testing_data
                )
            ]
        )
        mock_tower_instance.return_value.job_templates[0].name = "Mock"
        self.tower_server_test.sync()
        # assert that the survey has been updated
        updated_template = JobTemplate.objects.get(id=self.job_template_test.id,
                                                   tower_server=self.tower_server_test)
        self.assertDictEqual(self.new_survey, updated_template.survey)
        # check that the operation tower_survey_fields has been updated
        updated_operation = Operation.objects.get(id=self.create_operation_test.id)
        for field in updated_template.survey["spec"]:
            self.assertTrue(updated_operation.tower_survey_fields.filter(name=field["variable"], enabled=True).exists())

    @patch('service_catalog.models.tower_server.TowerServer._update_job_template_from_tower')
    @patch('towerlib.towerlib.Tower.get_job_template_by_id')
    @patch('service_catalog.models.tower_server.TowerServer.get_tower_instance')
    def test_sync_selected_job_template(self, mock_tower_instance, mock_get_job_template_by_id,
                                        mock_update_job_template_from_tower):
        self.job_template_test.tower_id = 20
        self.job_template_test.save()
        mock_tower_instance.return_value = MagicMock()
        mock_get_job_template_by_id.return_value = MagicMock(
            id=1,
            survey_spec=self.new_survey,
            _data=self.job_template_testing_data
        )
        self.tower_server_test.sync(job_template_id=self.job_template_test.id)
        mock_update_job_template_from_tower.assert_called()

    def test_update_job_template_from_tower(self):
        self.job_template_test.tower_id = 10
        self.job_template_test.save()
        job_template_from_tower = MagicMock(id=10,
                                            _data=self.job_template_testing_data,
                                            survey_spec=self.new_survey)
        job_template_from_tower.name = "tower_job_template_update"
        self.tower_server_test._update_job_template_from_tower(job_template_from_tower)
        self.job_template_test.refresh_from_db()
        self.assertEqual(self.job_template_test.name, "tower_job_template_update")
        self.assertEqual(self.job_template_test.survey, self.new_survey)
        self.assertEqual(self.job_template_test.tower_job_template_data, self.job_template_testing_data)
