import tempfile
from django.test.testcases import TransactionTestCase
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from rest_framework.test import APITestCase

from profiles.models import Organization, Scope, Role, Team
from service_catalog.models import TowerServer, JobTemplate, Operation, Service, Portfolio
from service_catalog.models.operations import OperationType


class BaseTestCommon(TransactionTestCase):

    def setUp(self):
        # Organization
        self.test_quota_scope_org = Organization.objects.create(name='Test Organization 1')
        self.test_quota_scope_org2 = Organization.objects.create(name='Test Organization 2')

        # Team
        self.test_quota_scope_team = Team.objects.create(name='Test Team 1', org=self.test_quota_scope_org)
        self.test_quota_scope_team2 = Team.objects.create(name='Test Team 2', org=self.test_quota_scope_org2)

        # Scopes
        self.test_quota_scope = Scope.objects.get(id=self.test_quota_scope_org.id)
        self.test_quota_scope2 = Scope.objects.get(id=self.test_quota_scope_org2.id)

        # ------------------------------
        # USERS
        # ------------------------------
        self.common_password = "p@ssw0rd"
        # staff user (default user for all tests)
        self.superuser = User.objects.create_superuser('admi1234', 'admin@hpe.com', self.common_password)
        self.superuser_2 = User.objects.create_superuser('admin_2', 'admin_2@hpe.com', self.common_password)
        self.client.login(username=self.superuser.username, password=self.common_password)
        # standard user
        self.standard_user = User.objects.create_user('stan1234', 'stan.1234@hpe.com', self.common_password)
        self.standard_user_2 = User.objects.create_user('other1234', 'other.guy@hpe.com', self.common_password)


        self.organization_admin_role = Role.objects.get(name="Organization manager")
        self.team_member_role = Role.objects.create(name="Team member for tests")
        self.team_member_role.permissions.add(Permission.objects.get_by_natural_key(codename="view_instance",app_label="service_catalog",model="instance"))
        self.team_member_role.permissions.add(Permission.objects.get_by_natural_key(codename="request_on_service",app_label="service_catalog",model="service"))
        self.team_member_role.permissions.add(Permission.objects.get_by_natural_key(codename="change_requestmessage",app_label="service_catalog",model="requestmessage"))
        self.team_member_role.permissions.add(Permission.objects.get_by_natural_key(codename="consume_quota_scope",app_label="profiles",model="scope"))
        self.test_quota_scope.add_user_in_role(self.standard_user, self.team_member_role)
        self.test_quota_scope_team.add_user_in_role(self.standard_user, self.team_member_role)
        # ------------------------------
        # Tower
        # ------------------------------
        self.tower_server_test = TowerServer.objects.create(name="tower-server-test", host="localhost", token="xxx")
        self.tower_server_test_2 = TowerServer.objects.create(name="tower-server-test-2", host="my-tower.com",
                                                              token="xxx")
        self.job_template_testing_data = {'id': 7, 'type': 'job_template', 'url': '/api/v2/job_templates/7/',
                                          'related': {'created_by': '/api/v2/users/1/',
                                                      'modified_by': '/api/v2/users/3/',
                                                      'labels': '/api/v2/job_templates/7/labels/',
                                                      'inventory': '/api/v2/inventories/1/',
                                                      'project': '/api/v2/projects/6/',
                                                      'organization': '/api/v2/organizations/1/',
                                                      'credentials': '/api/v2/job_templates/7/credentials/',
                                                      'last_job': '/api/v2/jobs/86/',
                                                      'jobs': '/api/v2/job_templates/7/jobs/',
                                                      'schedules': '/api/v2/job_templates/7/schedules/',
                                                      'activity_stream': '/api/v2/job_templates/7/activity_stream/',
                                                      'launch': '/api/v2/job_templates/7/launch/',
                                                      'webhook_key': '/api/v2/job_templates/7/webhook_key/',
                                                      'webhook_receiver': '',
                                                      'notification_templates_started': '/api/v2/job_templates/7/notification_templates_started/',
                                                      'notification_templates_success': '/api/v2/job_templates/7/notification_templates_success/',
                                                      'notification_templates_error': '/api/v2/job_templates/7/notification_templates_error/',
                                                      'access_list': '/api/v2/job_templates/7/access_list/',
                                                      'survey_spec': '/api/v2/job_templates/7/survey_spec/',
                                                      'object_roles': '/api/v2/job_templates/7/object_roles/',
                                                      'instance_groups': '/api/v2/job_templates/7/instance_groups/',
                                                      'slice_workflow_jobs': '/api/v2/job_templates/7/slice_workflow_jobs/',
                                                      'copy': '/api/v2/job_templates/7/copy/'}, 'summary_fields': {
                'organization': {'id': 1, 'name': 'Default', 'description': ''},
                'inventory': {'id': 1, 'name': 'Demo Inventory', 'description': '', 'has_active_failures': False,
                              'total_hosts': 1, 'hosts_with_active_failures': 0, 'total_groups': 0,
                              'has_inventory_sources': False, 'total_inventory_sources': 0,
                              'inventory_sources_with_failures': 0, 'organization_id': 1, 'kind': ''},
                'project': {'id': 6, 'name': 'Demo Project', 'description': '', 'status': 'successful',
                            'scm_type': 'git', 'allow_override': False},
                'last_job': {'id': 86, 'name': 'Demo Job Template', 'description': '',
                             'finished': '2021-08-30T14:40:08.529665Z', 'status': 'successful', 'failed': False},
                'last_update': {'id': 86, 'name': 'Demo Job Template', 'description': '', 'status': 'successful',
                                'failed': False},
                'created_by': {'id': 1, 'username': 'admin', 'first_name': '', 'last_name': ''},
                'modified_by': {'id': 3, 'username': 'admin', 'first_name': '', 'last_name': ''}, 'object_roles': {
                    'admin_role': {'description': 'Can manage all aspects of the job template', 'name': 'Admin',
                                   'id': 31},
                    'execute_role': {'description': 'May run the job template', 'name': 'Execute', 'id': 32},
                    'read_role': {'description': 'May view settings for the job template', 'name': 'Read', 'id': 33}},
                'user_capabilities': {'edit': True, 'delete': True, 'start': True, 'schedule': True, 'copy': True},
                'labels': {'count': 0, 'results': []}, 'survey': {'title': '', 'description': ''}, 'recent_jobs': [
                    {'id': 86, 'status': 'successful', 'finished': '2021-08-30T14:40:08.529665Z', 'canceled_on': None,
                     'type': 'job'},
                    {'id': 79, 'status': 'successful', 'finished': '2021-08-26T09:48:05.434378Z', 'canceled_on': None,
                     'type': 'job'},
                    {'id': 77, 'status': 'successful', 'finished': '2021-08-25T14:32:42.267931Z', 'canceled_on': None,
                     'type': 'job'},
                    {'id': 75, 'status': 'successful', 'finished': '2021-08-25T09:37:33.483015Z', 'canceled_on': None,
                     'type': 'job'},
                    {'id': 73, 'status': 'successful', 'finished': '2021-08-25T09:36:49.243095Z', 'canceled_on': None,
                     'type': 'job'},
                    {'id': 45, 'status': 'successful', 'finished': '2021-08-25T08:23:53.912737Z', 'canceled_on': None,
                     'type': 'job'},
                    {'id': 43, 'status': 'successful', 'finished': '2021-08-25T08:21:22.284012Z', 'canceled_on': None,
                     'type': 'job'},
                    {'id': 33, 'status': 'successful', 'finished': '2021-08-10T17:29:43.661219Z', 'canceled_on': None,
                     'type': 'job'},
                    {'id': 31, 'status': 'successful', 'finished': '2021-08-10T17:25:34.442519Z', 'canceled_on': None,
                     'type': 'job'},
                    {'id': 29, 'status': 'successful', 'finished': '2021-08-10T17:09:19.953059Z', 'canceled_on': None,
                     'type': 'job'}], 'credentials': [
                    {'id': 1, 'name': 'Demo Credential', 'description': '', 'kind': 'ssh', 'cloud': False}]},
                                          'created': '2021-07-05T15:27:26.413731Z',
                                          'modified': '2021-09-02T07:59:33.082124Z', 'name': 'Demo Job Template',
                                          'description': '', 'job_type': 'run', 'inventory': 1, 'project': 6,
                                          'playbook': 'hello_world.yml', 'scm_branch': '', 'forks': 0, 'limit': '',
                                          'verbosity': 0, 'extra_vars': '---', 'job_tags': '', 'force_handlers': False,
                                          'skip_tags': '', 'start_at_task': '', 'timeout': 0, 'use_fact_cache': False,
                                          'organization': 1, 'last_job_run': '2021-08-30T14:40:08.529665Z',
                                          'last_job_failed': False, 'next_job_run': None, 'status': 'successful',
                                          'execution_environment': None, 'host_config_key': '',
                                          'ask_scm_branch_on_launch': False, 'ask_diff_mode_on_launch': False,
                                          'ask_variables_on_launch': True, 'ask_limit_on_launch': False,
                                          'ask_tags_on_launch': False, 'ask_skip_tags_on_launch': False,
                                          'ask_job_type_on_launch': False, 'ask_verbosity_on_launch': False,
                                          'ask_inventory_on_launch': False, 'ask_credential_on_launch': False,
                                          'survey_enabled': True, 'become_enabled': False, 'diff_mode': False,
                                          'allow_simultaneous': False, 'custom_virtualenv': None, 'job_slice_count': 1,
                                          'webhook_service': '', 'webhook_credential': None}
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
                    "min": 8,
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
                    "required": False,
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
                                                            tower_server=self.tower_server_test,
                                                            tower_job_template_data=self.job_template_testing_data)
        self.job_template_test_2 = JobTemplate.objects.create(name="job-template-test",
                                                              survey=self.testing_survey,
                                                              tower_id=1,
                                                              tower_server=self.tower_server_test_2,
                                                              tower_job_template_data=self.job_template_testing_data)

        # ---------------------------------------------------
        # Portfolio test 1
        # ---------------------------------------------------
        self.portfolio_test_1 = Portfolio.objects.create(name="my-testing-portfolio")
        self.portfolio_test_1.image = tempfile.NamedTemporaryFile(suffix=".jpg").name
        self.portfolio_test_1.save()
        # ---------------------------------------------------
        # Portfolio test 1
        # ---------------------------------------------------
        self.portfolio_test_2 = Portfolio.objects.create(name="my-testing-portfolio",
                                                         parent_portfolio=self.portfolio_test_1)
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
        enabled_survey_fields = {
            'text_variable': True,
            'multiplechoice_variable': False,
            'multiselect_var': False,
            'textarea_var': False,
            'password_var': False,
            'float_var': False,
            'integer_var': False
        }
        self.create_operation_test.switch_tower_fields_enable_from_dict(enabled_survey_fields)
        self.update_operation_test = Operation.objects.create(name="update test",
                                                              service=self.service_test,
                                                              job_template=self.job_template_test,
                                                              type=OperationType.UPDATE)
        self.update_operation_test.switch_tower_fields_enable_from_dict(enabled_survey_fields)
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

        self.create_operation_test_2.switch_tower_fields_enable_from_dict(enabled_survey_fields)
        self.update_operation_test_2 = Operation.objects.create(name="update test",
                                                                service=self.service_test_2,
                                                                job_template=self.job_template_test,
                                                                type=OperationType.UPDATE)

        self.update_operation_test_2.switch_tower_fields_enable_from_dict(enabled_survey_fields)

        self.delete_operation_test_2 = Operation.objects.create(name="delete test",
                                                                service=self.service_test_2,
                                                                job_template=self.job_template_test,
                                                                type=OperationType.DELETE)
        # ---------------------------------------------------
        # Service with empty survey
        # ---------------------------------------------------
        self.testing_empty_survey = {
            "name": "test-empty-survey",
            "description": "test-empty-survey-description",
        }
        self.job_template_empty_survey_test = JobTemplate.objects.create(
            name="job-template-empty-survey-test",
            survey=self.testing_empty_survey,
            tower_id=2,
            tower_server=self.tower_server_test,
            tower_job_template_data=self.job_template_testing_data
        )
        self.service_empty_survey_test = Service.objects.create(name="service-empty-test",
                                                                description="description-of-service-test")
        self.service_empty_survey_test.image = tempfile.NamedTemporaryFile(suffix=".jpg").name
        self.service_empty_survey_test.save()
        self.create_operation_empty_survey_test = Operation.objects.create(
            name="create test empty survey",
            service=self.service_empty_survey_test,
            job_template=self.job_template_empty_survey_test,
            process_timeout_second=30
        )

        # ---------------------------------------------------
        # Small job template
        # ---------------------------------------------------
        self.testing_small_survey = {
            "name": "test-small-survey",
            "description": "test-small-survey-description",
            "spec":
                [
                    {
                        "question_name": "text",
                        "question_description": "text_des",
                        "required": True,
                        "type": "text",
                        "variable": "text",
                        "min": 0,
                        "max": 1024,
                        "default": "text_val",
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
                ]
        }
        self.job_template_small_survey_test = JobTemplate.objects.create(
            name="job-template-small-survey-test",
            survey=self.testing_small_survey,
            tower_id=3,
            tower_server=self.tower_server_test,
            tower_job_template_data=self.job_template_testing_data
        )


class BaseTest(TestCase, BaseTestCommon):
    pass


class BaseTestAPI(APITestCase, BaseTestCommon):
    pass
