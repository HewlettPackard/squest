import tempfile

from django.contrib.auth.models import User
from django.test import TestCase

from service_catalog.models import TowerServer, JobTemplate, Operation, Service
from service_catalog.models.operations import OperationType


class BaseTest(TestCase):

    def setUp(self):
        super(BaseTest, self).setUp()
        # ------------------------------
        # USERS
        # ------------------------------
        self.common_password = "p@ssw0rd"
        # staff user (default user for all tests)
        self.superuser = User.objects.create_superuser('admi1234', 'admin@hpe.com', self.common_password)
        self.client.login(username=self.superuser.username, password=self.common_password)
        # standard user
        self.standard_user = User.objects.create_user('stan1234', 'stan.1234@hpe.com', self.common_password)
        self.standard_user_2 = User.objects.create_user('other1234', 'other.guy@hpe.com', self.common_password)

        # ------------------------------
        # Tower
        # ------------------------------
        self.tower_server_test = TowerServer.objects.create(name="tower-server-test", host="localhost", token="xxx")
        self.testing_survey = {
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
                    "question_name": "String variable",
                    "required": True,
                    "type": "text",
                    "variable": "text_variable"
                },
                {
                    "choices": "choice1\nchoice2\nchoice3",
                    "default": "choice1",
                    "max": None,
                    "min": None,
                    "question_description": "",
                    "question_name": "List variable",
                    "required": True,
                    "type": "multiplechoice",
                    "variable": "multiplechoice_variable"
                },
                {
                    "question_name": "multiselect",
                    "question_description": "multiselect_des",
                    "required": True,
                    "type": "multiselect",
                    "variable": "multiselect_var",
                    "min": 0,
                    "max": 1024,
                    "formattedChoices": [
                        {
                            "choice": "multiselect_1",
                            "isDefault": False,
                            "id": 0
                        },
                        {
                            "choice": "multiselect_2",
                            "isDefault": True,
                            "id": 1
                        },
                        {
                            "choice": "multiselect_3",
                            "isDefault": True,
                            "id": 2
                        }
                    ],
                    "new_question": False,
                    "default": "multiselect_2\nmultiselect_3",
                    "choices": "multiselect_1\nmultiselect_2\nmultiselect_3"
                },
                {
                    "question_name": "textarea",
                    "question_description": "textarea_des",
                    "required": True,
                    "type": "textarea",
                    "variable": "textarea_var",
                    "min": 0,
                    "max": 1024,
                    "default": "textarea_val",
                    "choices": "",
                    "formattedChoices": [
                        {
                            "choice": "",
                            "isDefault": False,
                            "id": 0
                        }
                    ],
                    "new_question": False
                },
                {
                    "question_name": "password",
                    "question_description": "password_des",
                    "required": True,
                    "type": "password",
                    "variable": "password_var",
                    "min": 0,
                    "max": 1024,
                    "default": "password_val",
                    "choices": "",
                    "formattedChoices": [
                        {
                            "choice": "",
                            "isDefault": False,
                            "id": 0
                        }
                    ],
                    "new_question": False
                },
                {
                    "question_name": "integer",
                    "question_description": "integer_des",
                    "required": True,
                    "type": "integer",
                    "variable": "integer_var",
                    "min": 0,
                    "max": 1024,
                    "default": 1,
                    "choices": "",
                    "formattedChoices": [
                        {
                            "choice": "",
                            "isDefault": False,
                            "id": 0
                        }
                    ],
                    "new_question": False
                },
                {
                    "question_name": "float",
                    "question_description": "float_des",
                    "required": True,
                    "type": "float",
                    "variable": "float_var",
                    "min": 0,
                    "max": 1024,
                    "default": 1.5,
                    "choices": "",
                    "formattedChoices": [
                        {
                            "choice": "",
                            "isDefault": False,
                            "id": 0
                        }
                    ],
                    "new_question": False
                }
            ]
        }
        self.job_template_test = JobTemplate.objects.create(name="job-template-test",
                                                            survey=self.testing_survey,
                                                            tower_id=1,
                                                            tower_server=self.tower_server_test)

        # ---------------------------------------------------
        # Service test 1
        # ---------------------------------------------------
        self.service_test = Service.objects.create(name="service-test", description="description-of-service-test")
        self.service_test.image = tempfile.NamedTemporaryFile(suffix=".jpg").name
        self.service_test.save()

        self.create_operation_test = Operation.objects.create(name="create test",
                                                              service=self.service_test,
                                                              job_template=self.job_template_test,
                                                              process_timeout_second=20)

        self.create_operation_test.enabled_survey_fields = {
            'text_variable': True,
            'multiplechoice_variable': False,
            'multiselect_var': False,
            'textarea_var': False,
            'password_var': False,
            'float_var': False,
            'integer_var': False
        }
        self.create_operation_test.save()
        self.update_operation_test = Operation.objects.create(name="update test",
                                                              service=self.service_test,
                                                              job_template=self.job_template_test,
                                                              type=OperationType.UPDATE)
        self.update_operation_test.enabled_survey_fields = {
            'text_variable': True,
            'multiplechoice_variable': False,
            'multiselect_var': False,
            'textarea_var': False,
            'password_var': False,
            'float_var': False,
            'integer_var': False
        }
        self.update_operation_test.save()
        self.delete_operation_test = Operation.objects.create(name="delete test",
                                                              service=self.service_test,
                                                              job_template=self.job_template_test,
                                                              type=OperationType.DELETE)

        # ---------------------------------------------------
        # Service test 2
        # ---------------------------------------------------
        self.service_test_2 = Service.objects.create(name="service-test-2", description="description-of-service-test-2")
        self.service_test_2.image = tempfile.NamedTemporaryFile(suffix=".jpg").name
        self.service_test_2.save()

        self.create_operation_test_2 = Operation.objects.create(name="create test",
                                                                service=self.service_test_2,
                                                                job_template=self.job_template_test)
        self.create_operation_test_2.enabled_survey_fields = {
            'text_variable': True,
            'multiplechoice_variable': False,
            'multiselect_var': False,
            'textarea_var': False,
            'password_var': False,
            'float_var': False,
            'integer_var': False
        }
        self.create_operation_test_2.save()
        self.update_operation_test_2 = Operation.objects.create(name="update test",
                                                                service=self.service_test_2,
                                                                job_template=self.job_template_test,
                                                                type=OperationType.UPDATE)
        self.update_operation_test_2.enabled_survey_fields = {
            'text_variable': True,
            'multiplechoice_variable': False,
            'multiselect_var': False,
            'textarea_var': False,
            'password_var': False,
            'float_var': False,
            'integer_var': False
        }
        self.update_operation_test_2.save()
        self.delete_operation_test_2 = Operation.objects.create(name="delete test",
                                                                service=self.service_test_2,
                                                                job_template=self.job_template_test,
                                                                type=OperationType.DELETE)
