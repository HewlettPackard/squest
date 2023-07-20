from django.urls import reverse

from service_catalog.models import OperationType
from tests.test_service_catalog.base import BaseTest


class OperationEditTestCase(BaseTest):

    def setUp(self):
        super(OperationEditTestCase, self).setUp()
        args = {
            'service_id': self.service_test.id,
            'pk': self.update_operation_test.id,
        }
        self.url = reverse('service_catalog:operation_edit', kwargs=args)

    def test_edit_operation(self):
        data = {
            "name": "updated",
            "description": "updated description",
            "job_template": self.job_template_test.id,
            "type": OperationType.DELETE,
            "process_timeout_second": 60
        }
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(self.url, data=data)
        self.assertEqual(302, response.status_code)
        self.update_operation_test.refresh_from_db()
        self.assertEqual("updated", self.update_operation_test.name)
        self.assertEqual("updated description", self.update_operation_test.description)

    def test_edit_a_create_operation(self):
        args = {
            'service_id': self.service_test.id,
            'pk': self.create_operation_test.id,
        }
        url = reverse('service_catalog:operation_edit', kwargs=args)

        data = {
            "name": "updated",
            "description": "updated description",
            "job_template": self.job_template_test.id,
            "type": "CREATE",
            "process_timeout_second": 600
        }
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.create_operation_test.refresh_from_db()
        self.assertEqual("updated", self.create_operation_test.name)
        self.assertEqual("updated description", self.create_operation_test.description)

    def test_transform_create_into_edit(self):
        args = {
            'service_id': self.service_test.id,
            'pk': self.create_operation_test.id,
        }
        url = reverse('service_catalog:operation_edit', kwargs=args)

        data = {
            "name": "updated",
            "description": "updated description",
            "job_template": self.job_template_test.id,
            "type": OperationType.UPDATE,
            "process_timeout_second": 600
        }
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.create_operation_test.refresh_from_db()
        self.assertEqual("UPDATE", self.create_operation_test.type)

    def test_cannot_edit_service_operation_when_logout(self):
        self.client.logout()
        args = {
            'service_id': self.service_test.id,
            'pk': self.create_operation_test.id,
        }
        url = reverse('service_catalog:operation_edit', kwargs=args)

        data = {
            "name": "updated",
            "description": "updated description",
            "job_template": self.job_template_test.id,
            "type": OperationType.UPDATE,
            "process_timeout_second": 600
        }
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)

    def test_transform_delete_into_create(self):
        args = {
            'service_id': self.service_test.id,
            'pk': self.delete_operation_test.id,
        }
        url = reverse('service_catalog:operation_edit', kwargs=args)

        data = {
            "name": "updated",
            "description": "updated description",
            "job_template": self.job_template_test.id,
            "type": OperationType.CREATE,
            "process_timeout_second": 600
        }
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.delete_operation_test.refresh_from_db()
        self.assertEqual("CREATE", self.delete_operation_test.type)

    def test_transform_update_into_create(self):
        args = {
            'service_id': self.service_test.id,
            'pk': self.update_operation_test.id,
        }
        url = reverse('service_catalog:operation_edit', kwargs=args)

        data = {
            "name": "updated",
            "description": "updated description",
            "job_template": self.job_template_test.id,
            "type": "CREATE",
            "process_timeout_second": 600
        }
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.update_operation_test.refresh_from_db()
        self.assertEqual("CREATE", self.update_operation_test.type)

    def test_operation_edit_survey(self):
        args = {
            'service_id': self.service_test.id,
            'pk': self.update_operation_test.id,
        }
        url = reverse('service_catalog:operation_edit_survey', kwargs=args)
        data = {
            'form-0-id': self.update_operation_test.tower_survey_fields.get(name="text_variable").id,
            # 'form-0-enabled': "off",  not set means set to off
            'form-0-default': "default_var",
            'form-1-id': self.update_operation_test.tower_survey_fields.get(name="multiplechoice_variable").id,
            'form-1-is_customer_field': "on",
            'form-1-default': "default_var",
            'form-TOTAL_FORMS': 2,
            'form-INITIAL_FORMS': 2

        }
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertTrue(self.update_operation_test.tower_survey_fields.get(name="text_variable").is_customer_field)
        self.assertFalse(self.update_operation_test.tower_survey_fields.get(name="multiplechoice_variable").is_customer_field)
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.update_operation_test.refresh_from_db()
        self.assertFalse(self.update_operation_test.tower_survey_fields.get(name="text_variable").is_customer_field)
        self.assertTrue(self.update_operation_test.tower_survey_fields.get(name="multiplechoice_variable").is_customer_field)

    def test_update_survey_when_job_template_on_operation_changed(self):
        args = {
            'service_id': self.service_empty_survey_test.id,
            'pk': self.create_operation_empty_survey_test.id,
        }
        url = reverse('service_catalog:operation_edit', kwargs=args)

        data = {
            "name": "updated",
            "description": "updated description",
            "job_template": self.job_template_test.id,
            "type": "CREATE",
            "process_timeout_second": 600
        }
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, self.create_operation_empty_survey_test.tower_survey_fields.all().count())
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.create_operation_empty_survey_test.refresh_from_db()
        self.assertEqual("updated", self.create_operation_empty_survey_test.name)
        self.assertEqual("updated description", self.create_operation_empty_survey_test.description)
        self.assertEqual(self.job_template_test, self.create_operation_empty_survey_test.job_template)
        for key in _get_keys_from_survey(self.job_template_test.survey):
            self.assertTrue(self.create_operation_empty_survey_test.tower_survey_fields.filter(name=key).exists())

        data["job_template"] = self.job_template_small_survey_test.id
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.create_operation_empty_survey_test.refresh_from_db()
        self.assertEqual(self.job_template_small_survey_test, self.create_operation_empty_survey_test.job_template)
        for key in _get_keys_from_survey(self.job_template_small_survey_test.survey):
            self.assertTrue(self.create_operation_empty_survey_test.tower_survey_fields.filter(name=key).exists())


def _get_keys_from_survey(survey):
    fields = list()
    for field in survey['spec']:
        fields.append(field['variable'])
    return fields
