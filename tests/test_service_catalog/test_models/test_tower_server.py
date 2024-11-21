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
        mock_tower_instance.return_value = BaseTest.FakeTower(self.testing_survey, self.job_template_testing_data)
        self.tower_server_test.sync()
        mock_tower_instance.assert_called()
        # assert that the survey is the same
        self.assertDictEqual(self.testing_survey, self.job_template_test.survey)

    @patch('service_catalog.models.tower_server.TowerServer.get_tower_instance')
    def test_sync_survey_changed(self, mock_tower_instance):
        mock_tower_instance.return_value = BaseTest.FakeTower(self.new_survey, self.job_template_testing_data)
        self.tower_server_test.sync()
        # assert that the survey has been updated
        updated_template = JobTemplate.objects.get(name="job-template-test-1",
                                                   tower_server=self.tower_server_test)
        self.assertDictEqual(self.new_survey, updated_template.survey)
        # check that the operation tower_survey_fields has been updated
        updated_operation = Operation.objects.get(id=self.create_operation_test.id)
        for field in updated_template.survey["spec"]:
            self.assertTrue(updated_operation.tower_survey_fields.filter(variable=field["variable"], is_customer_field=True).exists())

    @patch('service_catalog.models.tower_server.TowerServer._update_job_template_from_tower')
    @patch('towerlib.towerlib.Tower.get_job_template_by_name')
    @patch('service_catalog.models.tower_server.TowerServer.get_tower_instance')
    def test_sync_selected_job_template(self, mock_tower_instance, mock_get_job_template_by_name,
                                        mock_update_job_template_from_tower):
        self.job_template_test.name = "test-survey"
        self.job_template_test.save()
        mock_tower_instance.return_value = BaseTest.FakeTower(self.testing_survey, self.job_template_testing_data)
        mock_get_job_template_by_name.return_value = MagicMock(
            id=1,
            survey_spec=self.new_survey,
            _data=self.job_template_testing_data
        )
        self.tower_server_test.sync(job_template_id=self.job_template_test.id)
        mock_update_job_template_from_tower.assert_called()

    @patch('service_catalog.models.tower_server.TowerServer.get_tower_instance')
    def test_update_job_template_from_tower(self, mock_tower_instance):
        self.job_template_test.tower_id = 10
        self.job_template_test.save()
        self.job_template_test.refresh_from_db()
        self.assertEqual(self.job_template_test.tower_id, 10)
        mock_tower_instance.return_value = BaseTest.FakeTower(self.new_survey, self.job_template_testing_data)
        self.tower_server_test._update_job_template_from_tower(self.job_template_test.name)
        self.job_template_test.refresh_from_db()
        self.assertEqual(self.job_template_test.tower_id, 1)
        self.assertEqual(self.job_template_test.survey, self.new_survey)
        self.assertEqual(self.job_template_test.tower_job_template_data, self.job_template_testing_data)

    @patch('towerlib.towerlib.Tower.get_job_template_by_name')
    @patch('service_catalog.models.tower_server.TowerServer.get_tower_instance')
    def test_update_non_existing_job_template_from_tower(self, mock_tower_instance, mock_get_job_template_by_name):
        self.job_template_test.name = "non-existing"
        self.job_template_test.save()
        job_template_id = self.job_template_test.id
        mock_tower_instance.return_value = BaseTest.FakeTower(self.testing_survey, self.job_template_testing_data)
        mock_get_job_template_by_name.return_value = None
        self.assertTrue(JobTemplate.objects.filter(id=job_template_id).exists())
        self.tower_server_test.sync(job_template_id)
        self.assertFalse(JobTemplate.objects.filter(id=job_template_id).exists())
