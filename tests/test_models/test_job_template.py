from unittest.mock import patch, MagicMock

from service_catalog.models import JobTemplate
from tests.base import BaseTest


class TestJobTemplate(BaseTest):

    def setUp(self):
        super(TestJobTemplate, self).setUp()

    @patch('service_catalog.models.tower_server.TowerServer.get_tower_instance')
    def set_up_tower(self, mock_tower_instance):
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
        self.job_templates = JobTemplate.objects.filter(tower_server=self.tower_server_test)

    def test_is_compliant(self):
        self.set_up_tower()
        job_templates = JobTemplate.objects.filter(tower_server=self.tower_server_test)
        self.assertTrue(job_templates[0].check_is_compliant())

    def test_is_not_compliant(self):
        self.job_template_testing_data['ask_variables_on_launch'] = False
        self.set_up_tower()
        job_templates = JobTemplate.objects.filter(tower_server=self.tower_server_test)
        self.assertFalse(job_templates[0].check_is_compliant())

