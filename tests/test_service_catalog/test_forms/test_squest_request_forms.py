from profiles.models import Quota
from service_catalog.forms import ServiceInstanceForm, ServiceRequestForm
from service_catalog.models import Instance
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestServiceInstanceForm(BaseTestRequest):

    def setUp(self):
        super(TestServiceInstanceForm, self).setUp()

    def test_first_form_create_instance(self):
        parameters = {
            "user": self.standard_user,
            "operation": self.create_operation_test
        }
        data = {
            "name": "instance_test",
            "quota_scope": self.test_quota_scope
        }
        form = ServiceInstanceForm(data=data, **parameters)
        saved_instance = form.save()
        self.assertEqual(saved_instance.service, self.service_test)
        self.assertEqual(saved_instance.requester, self.standard_user)

    def test_cannot_use_non_member_scope(self):
        parameters = {
            "user": self.standard_user_2,
            "operation": self.create_operation_test
        }
        data = {
            "name": "instance_test",
            "quota_scope": self.test_quota_scope
        }
        form = ServiceInstanceForm(data=data, **parameters)
        self.assertFalse(form.is_valid())
        self.assertTrue("quota_scope" in form.errors)


class TestServiceRequestForm(BaseTestRequest):

    def setUp(self):
        super(TestServiceRequestForm, self).setUp()
        self.empty_instance = Instance.objects.create(name="empty_instance",
                                                      service=self.service_test,
                                                      quota_scope=self.test_quota_scope,
                                                      requester=self.standard_user)

    def test_request_service(self):
        parameters = {
            "user": self.standard_user,
            "operation": self.create_operation_test,
            "quota_scope": self.test_quota_scope
        }
        data = {
            "text_variable": "test_variable"
        }
        form = ServiceRequestForm(data=data, **parameters)
        self.assertTrue(form.is_valid())
        new_request = form.save(self.empty_instance)
        self.assertEqual(new_request.instance, self.empty_instance)
        self.assertEqual(new_request.operation, self.create_operation_test)
        self.assertEqual(new_request.fill_in_survey, data)
        self.assertEqual(new_request.user, self.standard_user)

    def test_request_service_invalid_survey(self):
        parameters = {
            "user": self.standard_user,
            "operation": self.create_operation_test,
            "quota_scope": self.test_quota_scope
        }
        data = {
            "non_valid_var": "test_variable"
        }
        form = ServiceRequestForm(data=data, **parameters)
        self.assertFalse(form.is_valid())
        self.assertTrue("text_variable" in form.errors)

    def test_cannot_request_when_quota_limit_reached(self):
        # set a quota on cpu_attribute and link it to integer_var field
        Quota.objects.create(scope=self.test_quota_scope, limit=10, attribute_definition=self.cpu_attribute)
        integer_var_field = self.create_operation_test.tower_survey_fields.get(name="integer_var")
        integer_var_field.attribute_definition = self.cpu_attribute
        integer_var_field.save()

        # change the survey to ask only for the integer field
        enabled_survey_fields = {
            'text_variable': False,
            'multiplechoice_variable': False,
            'multiselect_var': False,
            'textarea_var': False,
            'password_var': False,
            'float_var': False,
            'integer_var': True
        }
        self.create_operation_test.switch_tower_fields_enable_from_dict(enabled_survey_fields)

        # ask more than the limit
        parameters = {
            "user": self.standard_user,
            "operation": self.create_operation_test,
            "quota_scope": self.test_quota_scope
        }
        data = {
            "integer_var": 12
        }
        form = ServiceRequestForm(data=data, **parameters)
        self.assertFalse(form.is_valid())
        self.assertIn("integer_var", form.errors)
        self.assertIn("Ensure this value is less than or equal to 10", form.errors["integer_var"][0])
