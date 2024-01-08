from django.contrib.auth.models import User

from service_catalog.api.serializers import ServiceRequestSerializer, OperationRequestSerializer
from service_catalog.models import InstanceState
from tests.setup import SetupInstance

from django.test import override_settings


class TestSurveyValidatorDay1Serializer(SetupInstance):

    def setUp(self):
        SetupInstance.setUp(self)
        self.operation_create_1.validators = 'survey_test.Validator1,survey_test.Validator2'
        self.operation_create_1.save()
        self.superuser = User.objects.create_superuser(username='superuser')

    @override_settings(SURVEY_VALIDATOR_PATH='tests/test_plugins/survey_validators_test')
    def test_injected_data_are_good(self):
        self.operation_create_1.validators = 'survey_test.ValidatorDay1'
        self.operation_create_1.save()
        data = {
            "squest_instance_name": "instance test",
            "quota_scope": self.org1.id,
            'request_comment': 'comment day1',
            "fill_in_survey": {
                "vcpu": 1,
                "ram": 1
            }
        }
        serializer = ServiceRequestSerializer(operation=self.operation_create_1, user=self.superuser, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['__all__'][0],
                         "Everything is good, it's just a message to be sure that code was executed")

    @override_settings(SURVEY_VALIDATOR_PATH='tests/test_plugins/survey_validators_test')
    def test_fail_with_0_0(self):
        data = {
            "squest_instance_name": "instance test",
            "quota_scope": self.org1.id,
            "request_comment": "None",
            "fill_in_survey": {
                "vcpu": 0,
                "ram": 0
            }
        }
        serializer = ServiceRequestSerializer(operation=self.operation_create_1, user=self.superuser, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['__all__'][0], 'ram and vCPU are both equal to 0')

    @override_settings(SURVEY_VALIDATOR_PATH='tests/test_plugins/survey_validators_test')
    def test_fail_with_ram_1_and_cpu_0(self):
        data = {
            "squest_instance_name": "instance test",
            "quota_scope": self.org1.id,
            "request_comment": "None",
            "fill_in_survey": {
                "vcpu": 0,
                "ram": 1
            }
        }
        serializer = ServiceRequestSerializer(operation=self.operation_create_1, user=self.superuser, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['vcpu'][0], 'vCPU is equal to 0')

    @override_settings(SURVEY_VALIDATOR_PATH='tests/test_plugins/survey_validators_test')
    def test_success_with_1_1(self):
        data = {
            "squest_instance_name": "instance test",
            "quota_scope": self.org1.id,
            "request_comment": "None",
            "fill_in_survey": {
                "vcpu": 1,
                "ram": 1
            }
        }
        serializer = ServiceRequestSerializer(operation=self.operation_create_1, user=self.superuser, data=data)
        self.assertTrue(serializer.is_valid())


class TestSurveyValidatorDay2Serializer(SetupInstance):

    def setUp(self):
        SetupInstance.setUp(self)
        self.operation_update_1.validators = 'survey_test.Validator1,survey_test.Validator2'
        self.operation_update_1.save()
        self.superuser = User.objects.create_superuser(username='superuser')
        self.client.force_login(user=self.superuser)
        self.instance_1_org1.state = InstanceState.AVAILABLE
        self.instance_1_org1.service = self.operation_update_1.service
        self.instance_1_org1.save()

    @override_settings(SURVEY_VALIDATOR_PATH='tests/test_plugins/survey_validators_test')
    def test_injected_data_are_good(self):
        self.operation_update_1.validators = 'survey_test.ValidatorDay2'
        self.operation_update_1.save()
        data = {
            'request_comment': 'comment day2',
            "fill_in_survey": {
                "vcpu": 1,
                "ram": 1
            }
        }
        form = OperationRequestSerializer(operation=self.operation_update_1, instance=self.instance_1_org1,
                                          user=self.superuser, data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'][0],
                         "Everything is good, it's just a message to be sure that code was executed")

    @override_settings(SURVEY_VALIDATOR_PATH='tests/test_plugins/survey_validators_test')
    def test_fail_with_0_0(self):
        data = {
            "fill_in_survey": {
                "vcpu": 0,
                "ram": 0
            }
        }
        form = OperationRequestSerializer(operation=self.operation_update_1, instance=self.instance_1_org1,
                                          user=self.superuser, data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'][0], 'ram and vCPU are both equal to 0')

    @override_settings(SURVEY_VALIDATOR_PATH='tests/test_plugins/survey_validators_test')
    def test_fail_with_ram_1_and_cpu_0(self):
        data = {
            "fill_in_survey": {
                "vcpu": 0,
                "ram": 1
            }
        }
        form = OperationRequestSerializer(operation=self.operation_update_1, instance=self.instance_1_org1,
                                          user=self.superuser, data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['vcpu'][0], 'vCPU is equal to 0')

    @override_settings(SURVEY_VALIDATOR_PATH='tests/test_plugins/survey_validators_test')
    def test_success_with_1_1(self):
        data = {
            "fill_in_survey": {
                "vcpu": 1,
                "ram": 1
            }
        }
        form = OperationRequestSerializer(operation=self.operation_update_1, instance=self.instance_1_org1,
                                          user=self.superuser, data=data)
        self.assertTrue(form.is_valid())
