from unittest.mock import patch, MagicMock

from service_catalog.models import JobTemplate, ExceptionServiceCatalog
from tests.test_service_catalog.base import BaseTest


class TestJobTemplate(BaseTest):

    def setUp(self):
        super(TestJobTemplate, self).setUp()

    @patch('service_catalog.models.ansiblecontroller.AnsibleController.get_remote_instance')
    def set_up_ansible_controller(self, mock_remote_instance):
        mock_remote_instance.return_value = MagicMock(
            job_templates=[
                MagicMock(
                    id=1,
                    survey_spec=self.testing_survey,
                    _data=self.job_template_testing_data
                )
            ]
        )
        mock_remote_instance.return_value.job_templates[0].name = "Mock"
        self.ansible_controller_test.sync()
        self.job_templates = JobTemplate.objects.filter(ansible_controller=self.ansible_controller_test)

    def test_is_compliant(self):
        self.set_up_ansible_controller()
        job_templates = JobTemplate.objects.filter(ansible_controller=self.ansible_controller_test)
        self.assertTrue(job_templates[0].check_is_compliant())

    def test_is_not_compliant(self):
        self.job_template_testing_data['ask_variables_on_launch'] = False
        self.set_up_ansible_controller()
        job_templates = JobTemplate.objects.filter(ansible_controller=self.ansible_controller_test)
        self.assertFalse(job_templates[0].check_is_compliant())

    @patch('service_catalog.models.ansiblecontroller.AnsibleController.get_remote_instance')
    def test_execute_no_job_template_returned(self, mock_remote_instance):
        mock_remote_instance.return_value.get_job_template_by_id.return_value = None
        with self.assertRaises(ExceptionServiceCatalog.JobTemplateNotFound):
            self.job_template_test.execute(extra_vars={"test_var": "test_val"})

    @patch('service_catalog.models.ansiblecontroller.AnsibleController.get_remote_instance')
    def test_execute_job_template_returned(self, mock_remote_instance):
        mock_remote_instance.return_value = MagicMock(name="mock_remote_instance")
        mock_job_template = MagicMock(name="mock_job_template")
        mock_remote_instance.return_value.get_job_template_by_id.return_value = mock_job_template
        mock_job_template.launch.return_value.id = 5
        self.job_template_test.execute(extra_vars={"test_var": "test_val"})
        mock_job_template.launch.assert_called()
