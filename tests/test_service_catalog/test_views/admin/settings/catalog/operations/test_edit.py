from django.urls import reverse

from service_catalog.models import OperationType
from tests.test_service_catalog.base import BaseTest


class OperationEditTestCase(BaseTest):

    def setUp(self):
        super(OperationEditTestCase, self).setUp()
        args = {
            'service_id': self.service_test.id,
            'operation_id': self.update_operation_test.id,
        }
        self.url = reverse('service_catalog:edit_service_operation', kwargs=args)

    def test_edit_operation(self):
        data = {
            "name": "updated",
            "description": "updated description",
            "job_template": self.job_template_test.id,
            "type": OperationType.DELETE,
            "process_timeout_second": 60
        }
        response = self.client.post(self.url, data=data)
        self.assertEquals(302, response.status_code)
        self.update_operation_test.refresh_from_db()
        self.assertEquals("updated", self.update_operation_test.name)
        self.assertEquals("updated description", self.update_operation_test.description)

    def test_edit_a_create_operation(self):
        args = {
            'service_id': self.service_test.id,
            'operation_id': self.create_operation_test.id,
        }
        url = reverse('service_catalog:edit_service_operation', kwargs=args)

        data = {
            "name": "updated",
            "description": "updated description",
            "job_template": self.job_template_test.id,
            "type": "CREATE",
            "process_timeout_second": 600
        }
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.create_operation_test.refresh_from_db()
        self.assertEquals("updated", self.create_operation_test.name)
        self.assertEquals("updated description", self.create_operation_test.description)

    def test_transform_create_into_edit(self):
        args = {
            'service_id': self.service_test.id,
            'operation_id': self.create_operation_test.id,
        }
        url = reverse('service_catalog:edit_service_operation', kwargs=args)

        data = {
            "name": "updated",
            "description": "updated description",
            "job_template": self.job_template_test.id,
            "type": OperationType.UPDATE,
            "process_timeout_second": 600
        }
        response = self.client.post(url, data=data)
        self.assertEquals(200, response.status_code)
        self.create_operation_test.refresh_from_db()
        self.assertEquals("CREATE", self.create_operation_test.type)

    def test_cannot_edit_service_operation_when_logout(self):
        self.client.logout()
        args = {
            'service_id': self.service_test.id,
            'operation_id': self.create_operation_test.id,
        }
        url = reverse('service_catalog:edit_service_operation', kwargs=args)

        data = {
            "name": "updated",
            "description": "updated description",
            "job_template": self.job_template_test.id,
            "type": OperationType.UPDATE,
            "process_timeout_second": 600
        }
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)

    def test_transform_delete_into_create(self):
        args = {
            'service_id': self.service_test.id,
            'operation_id': self.delete_operation_test.id,
        }
        url = reverse('service_catalog:edit_service_operation', kwargs=args)

        data = {
            "name": "updated",
            "description": "updated description",
            "job_template": self.job_template_test.id,
            "type": OperationType.CREATE,
            "process_timeout_second": 600
        }
        response = self.client.post(url, data=data)
        self.assertEquals(200, response.status_code)
        self.delete_operation_test.refresh_from_db()
        self.assertEquals("DELETE", self.delete_operation_test.type)

    def test_transform_update_into_create(self):
        args = {
            'service_id': self.service_test.id,
            'operation_id': self.update_operation_test.id,
        }
        url = reverse('service_catalog:edit_service_operation', kwargs=args)

        data = {
            "name": "updated",
            "description": "updated description",
            "job_template": self.job_template_test.id,
            "type": "CREATE",
            "process_timeout_second": 600
        }
        response = self.client.post(url, data=data)
        self.assertEquals(200, response.status_code)
        self.update_operation_test.refresh_from_db()
        self.assertEquals("UPDATE", self.update_operation_test.type)

    def test_service_operation_edit_survey(self):
        args = {
            'service_id': self.service_test.id,
            'operation_id': self.update_operation_test.id,
        }
        url = reverse('service_catalog:service_operation_edit_survey', kwargs=args)
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
        url = reverse('service_catalog:service_operation_edit_survey', kwargs=args)
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
        url = reverse('service_catalog:service_operation_edit_survey', kwargs=args)
        data = {
            'non_existing': True,
            'non_existing_2': True
        }
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.update_operation_test.refresh_from_db()
        self.assertTrue("non_existing" not in self.update_operation_test.enabled_survey_fields)
        self.assertTrue("non_existing_2" not in self.update_operation_test.enabled_survey_fields)

    def test_update_survey_when_job_template_on_operation_changed(self):
        args = {
            'service_id': self.service_empty_survey_test.id,
            'operation_id': self.create_operation_empty_survey_test.id,
        }
        url = reverse('service_catalog:edit_service_operation', kwargs=args)

        data = {
            "name": "updated",
            "description": "updated description",
            "job_template": self.job_template_test.id,
            "type": "CREATE",
            "process_timeout_second": 600
        }
        self.assertEquals({}, self.create_operation_empty_survey_test.enabled_survey_fields)
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.create_operation_empty_survey_test.refresh_from_db()
        self.assertEquals("updated", self.create_operation_empty_survey_test.name)
        self.assertEquals("updated description", self.create_operation_empty_survey_test.description)
        self.assertEquals(self.job_template_test, self.create_operation_empty_survey_test.job_template)
        self.assertEquals(
            set(_get_keys_from_survey(self.job_template_test.survey)),
            set(self.create_operation_empty_survey_test.enabled_survey_fields.keys())
        )

        data["job_template"] = self.job_template_small_survey_test.id
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.create_operation_empty_survey_test.refresh_from_db()
        self.assertEquals(self.job_template_small_survey_test, self.create_operation_empty_survey_test.job_template)
        self.assertEquals(
            set(_get_keys_from_survey(self.job_template_small_survey_test.survey)),
            set(self.create_operation_empty_survey_test.enabled_survey_fields.keys())
        )


def _get_keys_from_survey(survey):
    fields = list()
    for field in survey['spec']:
        fields.append(field['variable'])
    return fields
