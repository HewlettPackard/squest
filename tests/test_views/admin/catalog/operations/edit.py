from django.urls import reverse

from tests.base import BaseTest


class OperationEditTestCase(BaseTest):

    def setUp(self):
        super(OperationEditTestCase, self).setUp()
        args = {
            'service_id': self.service_test.id,
            'operation_id': self.update_operation_test.id,
        }
        self.url = reverse('edit_service_operation', kwargs=args)

    def test_edit_operation(self):
        data = {
            "name": "updated",
            "description": "updated description",
            "job_template": self.job_template_test.name,
            "type": "DELETE",
            "process_timeout_second": 60
        }
        response = self.client.post(self.url, data=data)
        self.assertEquals(302, response.status_code)
        self.update_operation_test.refresh_from_db()
        self.assertEquals("updated", self.update_operation_test.name)
        self.assertEquals("updated description", self.update_operation_test.description)

    def test_service_operation_edit_survey(self):
        args = {
            'service_id': self.service_test.id,
            'operation_id': self.update_operation_test.id,
        }
        url = reverse('service_operation_edit_survey', kwargs=args)
        data = {
            'text_variable': True,
            'multiplechoice_variable': True
        }
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.update_operation_test.refresh_from_db()
        self.assertTrue("text_variable" in self.update_operation_test.enabled_survey_fields)
        self.assertTrue(self.update_operation_test.enabled_survey_fields["text_variable"])
        self.assertTrue("multiplechoice_variable" in self.update_operation_test.enabled_survey_fields)
        self.assertTrue(self.update_operation_test.enabled_survey_fields["multiplechoice_variable"])

    def test_service_operation_edit_survey_edit_only_one_filed(self):
        args = {
            'service_id': self.service_test.id,
            'operation_id': self.update_operation_test.id,
        }
        url = reverse('service_operation_edit_survey', kwargs=args)
        data = {
            'text_variable': True,
        }
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.update_operation_test.refresh_from_db()
        self.assertTrue("text_variable" in self.update_operation_test.enabled_survey_fields)
        self.assertTrue(self.update_operation_test.enabled_survey_fields["text_variable"])

    def test_service_operation_edit_survey_non_existing_flag(self):
        args = {
            'service_id': self.service_test.id,
            'operation_id': self.update_operation_test.id,
        }
        url = reverse('service_operation_edit_survey', kwargs=args)
        data = {
            'non_existing': True,
            'non_existing_2': True
        }
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.update_operation_test.refresh_from_db()
        self.assertTrue("non_existing" not in self.update_operation_test.enabled_survey_fields)
        self.assertTrue("non_existing_2" not in self.update_operation_test.enabled_survey_fields)
