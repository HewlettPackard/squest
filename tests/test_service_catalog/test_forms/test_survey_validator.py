from django.contrib.auth.models import User

from profiles.models import Scope
from service_catalog.forms import ServiceRequestForm, OperationRequestForm
from service_catalog.models import InstanceState
from tests.setup import  SetupInstance

from django.test import override_settings


class TestSurveyValidatorDay1Form(SetupInstance):

    def setUp(self):
        SetupInstance.setUp(self)
        self.operation_create_1.validators = 'survey_test.Validator1,survey_test.Validator2'
        self.operation_create_1.save()
        self.superuser = User.objects.create_superuser(username='superuser')
        self.client.force_login(user=self.superuser)
        self.parameters = {
            'operation': self.operation_create_1,
            'quota_scope': Scope.objects.get(id=self.org1.id),
            'user': self.superuser,
            'instance_name': "instance test"
        }

    @override_settings(SURVEY_VALIDATOR_PATH='tests/test_plugins/survey_validators_test')
    def test_injected_data_are_good(self):
        self.operation_create_1.validators = 'survey_test.ValidatorDay1'
        self.operation_create_1.save()
        data = {
            'request_comment': 'comment day1',
            'vcpu': 1,
            'ram': 1
        }
        form = ServiceRequestForm(data, **self.parameters)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'].data[0].message,
                         "Everything is good, it's just a message to be sure that code was executed")

    @override_settings(SURVEY_VALIDATOR_PATH='tests/test_plugins/survey_validators_test')
    def test_fail_with_0_0(self):
        data = {
            'vcpu': 0,
            'ram': 0
        }
        form = ServiceRequestForm(data, **self.parameters)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'].data[0].message, 'ram and vCPU are both equal to 0')

    @override_settings(SURVEY_VALIDATOR_PATH='tests/test_plugins/survey_validators_test')
    def test_fail_with_ram_1_and_cpu_0(self):
        data = {
            'vcpu': 0,
            'ram': 1
        }
        form = ServiceRequestForm(data, **self.parameters)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['vcpu'].data[0].message, 'vCPU is equal to 0')

    @override_settings(SURVEY_VALIDATOR_PATH='tests/test_plugins/survey_validators_test')
    def test_success_with_1_1(self):
        data = {
            'vcpu': 1,
            'ram': 1
        }
        form = ServiceRequestForm(data, **self.parameters)
        self.assertTrue(form.is_valid())


class TestSurveyValidatorDay2Form(SetupInstance):

    def setUp(self):
        SetupInstance.setUp(self)
        self.operation_update_1.validators = 'survey_test.Validator1,survey_test.Validator2'
        self.operation_update_1.save()
        self.superuser = User.objects.create_superuser(username='superuser')
        self.client.force_login(user=self.superuser)
        self.instance_1_org1.state = InstanceState.AVAILABLE
        self.instance_1_org1.save()
        self.parameters = {
            'instance': self.instance_1_org1,
            'operation': self.operation_update_1
        }

    @override_settings(SURVEY_VALIDATOR_PATH='tests/test_plugins/survey_validators_test')
    def test_injected_data_are_good(self):
        self.operation_update_1.validators = 'survey_test.ValidatorDay2'
        self.operation_update_1.save()
        data = {
            'request_comment': 'comment day2',
            'vcpu': 1,
            'ram': 1
        }
        form = OperationRequestForm(user=self.superuser, data=data, **self.parameters)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'].data[0].message,
                         "Everything is good, it's just a message to be sure that code was executed")

    @override_settings(SURVEY_VALIDATOR_PATH='tests/test_plugins/survey_validators_test')
    def test_fail_with_0_0(self):
        data = {
            'vcpu': 0,
            'ram': 0
        }
        form = OperationRequestForm(user=self.superuser, data=data, **self.parameters)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'].data[0].message, 'ram and vCPU are both equal to 0')

    @override_settings(SURVEY_VALIDATOR_PATH='tests/test_plugins/survey_validators_test')
    def test_fail_with_ram_1_and_cpu_0(self):
        data = {
            'vcpu': 0,
            'ram': 1
        }
        form = OperationRequestForm(user=self.superuser, data=data, **self.parameters)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['vcpu'].data[0].message, 'vCPU is equal to 0')

    @override_settings(SURVEY_VALIDATOR_PATH='tests/test_plugins/survey_validators_test')
    def test_success_with_1_1(self):
        data = {
            'vcpu': 1,
            'ram': 1
        }
        form = OperationRequestForm(user=self.superuser, data=data, **self.parameters)
        self.assertTrue(form.is_valid())
