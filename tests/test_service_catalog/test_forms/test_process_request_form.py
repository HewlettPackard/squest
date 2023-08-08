from service_catalog.forms.process_request_form import ProcessRequestForm
from service_catalog.models import Inventory, Credential
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestProcessRequestForm(BaseTestRequest):

    def setUp(self):
        super(TestProcessRequestForm, self).setUp()

        self.test_request.operation.job_template.remote_job_template_data = {
            "id": 7,
            "type": "job_template",
            "url": "/api/v2/job_templates/7/",
            "related": {
                "created_by": "/api/v2/users/1/",
                "modified_by": "/api/v2/users/1/",
                "labels": "/api/v2/job_templates/7/labels/",
                "inventory": "/api/v2/inventories/1/",
                "project": "/api/v2/projects/6/",
                "organization": "/api/v2/organizations/1/",
                "credentials": "/api/v2/job_templates/7/credentials/",
                "last_job": "/api/v2/jobs/465/",
                "jobs": "/api/v2/job_templates/7/jobs/",
                "schedules": "/api/v2/job_templates/7/schedules/",
                "activity_stream": "/api/v2/job_templates/7/activity_stream/",
                "launch": "/api/v2/job_templates/7/launch/",
                "webhook_key": "/api/v2/job_templates/7/webhook_key/",
                "webhook_receiver": "",
                "notification_templates_started": "/api/v2/job_templates/7/notification_templates_started/",
                "notification_templates_success": "/api/v2/job_templates/7/notification_templates_success/",
                "notification_templates_error": "/api/v2/job_templates/7/notification_templates_error/",
                "access_list": "/api/v2/job_templates/7/access_list/",
                "survey_spec": "/api/v2/job_templates/7/survey_spec/",
                "object_roles": "/api/v2/job_templates/7/object_roles/",
                "instance_groups": "/api/v2/job_templates/7/instance_groups/",
                "slice_workflow_jobs": "/api/v2/job_templates/7/slice_workflow_jobs/",
                "copy": "/api/v2/job_templates/7/copy/"
            },
            "summary_fields": {
                "organization": {
                    "id": 1,
                    "name": "Default",
                    "description": ""
                },
                "inventory": {
                    "id": 1,
                    "name": "Demo Inventory",
                    "description": "",
                    "has_active_failures": False,
                    "total_hosts": 1,
                    "hosts_with_active_failures": 0,
                    "total_groups": 0,
                    "has_inventory_sources": False,
                    "total_inventory_sources": 0,
                    "inventory_sources_with_failures": 0,
                    "organization_id": 1,
                    "kind": ""
                },
                "project": {
                    "id": 6,
                    "name": "Demo Project",
                    "description": "",
                    "status": "successful",
                    "scm_type": "git",
                    "allow_override": False
                },
                "last_job": {
                    "id": 465,
                    "name": "Demo Job Template",
                    "description": "",
                    "finished": "2022-09-28T17:00:19.857515Z",
                    "status": "successful",
                    "failed": False
                },
                "last_update": {
                    "id": 465,
                    "name": "Demo Job Template",
                    "description": "",
                    "status": "successful",
                    "failed": False
                },
                "created_by": {
                    "id": 1,
                    "username": "admin",
                    "first_name": "",
                    "last_name": ""
                },
                "modified_by": {
                    "id": 1,
                    "username": "admin",
                    "first_name": "",
                    "last_name": ""
                },
                "object_roles": {
                    "admin_role": {
                        "description": "Can manage all aspects of the job template",
                        "name": "Admin",
                        "id": 31
                    },
                    "execute_role": {
                        "description": "May run the job template",
                        "name": "Execute",
                        "id": 32
                    },
                    "read_role": {
                        "description": "May view settings for the job template",
                        "name": "Read",
                        "id": 33
                    }
                },
                "user_capabilities": {
                    "edit": True,
                    "delete": True,
                    "start": True,
                    "schedule": True,
                    "copy": True
                },
                "labels": {
                    "count": 0,
                    "results": []
                },
                "survey": {
                    "title": "",
                    "description": ""
                },
                "recent_jobs": [
                ],
                "credentials": [
                    {
                        "id": 1,
                        "name": "Demo Credential",
                        "description": "",
                        "kind": "ssh",
                        "cloud": False
                    }
                ]
            },
            "created": "2022-09-05T14:09:32.026758Z",
            "modified": "2022-09-30T13:23:05.966926Z",
            "name": "Demo Job Template",
            "description": "",
            "job_type": "run",
            "inventory": 1,
            "project": 6,
            "playbook": "hello_world.yml",
            "scm_branch": "",
            "forks": 0,
            "limit": "",
            "verbosity": 0,
            "extra_vars": "---",
            "job_tags": "",
            "force_handlers": False,
            "skip_tags": "",
            "start_at_task": "",
            "timeout": 0,
            "use_fact_cache": False,
            "organization": 1,
            "last_job_run": "2022-09-28T17:00:19.857515Z",
            "last_job_failed": False,
            "next_job_run": None,
            "status": "successful",
            "execution_environment": None,
            "host_config_key": "",
            "ask_scm_branch_on_launch": False,
            "ask_diff_mode_on_launch": True,
            "ask_variables_on_launch": True,
            "ask_limit_on_launch": True,
            "ask_tags_on_launch": True,
            "ask_skip_tags_on_launch": True,
            "ask_job_type_on_launch": True,
            "ask_verbosity_on_launch": True,
            "ask_inventory_on_launch": True,
            "ask_credential_on_launch": True,
            "survey_enabled": True,
            "become_enabled": False,
            "diff_mode": False,
            "allow_simultaneous": False,
            "custom_virtualenv": None,
            "job_slice_count": 1,
            "webhook_service": "",
            "webhook_credential": None
        }

    def test_remote_job_template_data_key_enabled(self):
        process_request_form = ProcessRequestForm(request=self.test_request, user=self.superuser)
        self.assertTrue(process_request_form.remote_job_template_data_key_enabled("ask_diff_mode_on_launch"))
        self.assertFalse(process_request_form.remote_job_template_data_key_enabled("ask_scm_branch_on_launch"))
        self.assertFalse(process_request_form.remote_job_template_data_key_enabled("does_not_exist"))

    def test_get_inventories_as_choices(self):
        inventory_test_1 = Inventory.objects.create(name="inventory_test_1",
                                                    remote_id=1, ansible_controller=self.ansible_controller_test)
        inventory_test_2 = Inventory.objects.create(name="inventory_test_2",
                                                    remote_id=2, ansible_controller=self.ansible_controller_test)
        inventory_test_3 = Inventory.objects.create(name="inventory_test_3",
                                                    remote_id=2, ansible_controller=self.ansible_controller_test_2)

        expected_choices = [(inventory_test_1.ansible_controller_id, inventory_test_1.name),
                            (inventory_test_2.ansible_controller_id, inventory_test_2.name)]
        process_request_form = ProcessRequestForm(request=self.test_request, user=self.superuser)
        self.assertEqual(process_request_form.get_inventories_as_choices(), expected_choices)

    def test_get_credentials_as_choices(self):
        credential_test_1 = Credential.objects.create(name="credential_test_1",
                                                      remote_id=1, ansible_controller=self.ansible_controller_test)
        credential_test_2 = Credential.objects.create(name="credential_test_2",
                                                      remote_id=2, ansible_controller=self.ansible_controller_test)
        credential_test_3 = Credential.objects.create(name="credential_test_3",
                                                      remote_id=2, ansible_controller=self.ansible_controller_test_2)

        expected_choices = [(credential_test_1.ansible_controller_id, credential_test_1.name),
                            (credential_test_2.ansible_controller_id, credential_test_2.name)]
        process_request_form = ProcessRequestForm(request=self.test_request, user=self.superuser)
        self.assertEqual(process_request_form.get_credentials_as_choices(), expected_choices)

    def test_get_templated_initial(self):
        # test simple string with no jinja
        jinja_string = "test"
        expected_result = "test"
        process_request_form = ProcessRequestForm(request=self.test_request, user=self.superuser)
        self.assertEqual(process_request_form._get_templated_initial(jinja_string), expected_result)

        # test instance based jinja
        self.test_request.instance.spec = {
            "os": "ubuntu"
        }
        self.test_request.instance.save()
        jinja_string = "{{ request.instance.spec.os }}"
        expected_result = "ubuntu"
        process_request_form = ProcessRequestForm(request=self.test_request, user=self.superuser)
        self.assertEqual(process_request_form._get_templated_initial(jinja_string), expected_result)

        # test non-existing flag in the instance
        jinja_string = "{{ request.instance.spec.non_existing_key }}"
        expected_result = ""
        process_request_form = ProcessRequestForm(request=self.test_request, user=self.superuser)
        self.assertEqual(process_request_form._get_templated_initial(jinja_string), expected_result)

        # test invalid jinja
        jinja_string = "{% for value in request.non_existing_key %}"
        expected_result = ""
        process_request_form = ProcessRequestForm(request=self.test_request, user=self.superuser)
        self.assertEqual(process_request_form._get_templated_initial(jinja_string), expected_result)

    def test_is_all_field_visible_to_admin_or_user_only(self):
        # test with all field to user
        enabled_survey_fields = {
            'text_variable': True,
            'multiplechoice_variable': True,
            'multiselect_var': True,
            'textarea_var': True,
            'password_var': True,
            'float_var': True,
            'integer_var': True
        }
        self.create_operation_test.switch_survey_fields_enable_from_dict(enabled_survey_fields)
        process_request_form = ProcessRequestForm(request=self.test_request, user=self.superuser)
        self.assertTrue(process_request_form.is_all_field_visible_to_admin_or_user_only())

        # test with all field to admin
        enabled_survey_fields = {
            'text_variable': False,
            'multiplechoice_variable': False,
            'multiselect_var': False,
            'textarea_var': False,
            'password_var': False,
            'float_var': False,
            'integer_var': False
        }
        self.create_operation_test.switch_survey_fields_enable_from_dict(enabled_survey_fields)
        process_request_form = ProcessRequestForm(request=self.test_request, user=self.superuser)
        self.assertTrue(process_request_form.is_all_field_visible_to_admin_or_user_only())

        # test with at least one field to dmin
        enabled_survey_fields = {
            'text_variable': True,
            'multiplechoice_variable': False,
            'multiselect_var': False,
            'textarea_var': False,
            'password_var': False,
            'float_var': False,
            'integer_var': False
        }
        self.create_operation_test.switch_survey_fields_enable_from_dict(enabled_survey_fields)
        process_request_form = ProcessRequestForm(request=self.test_request, user=self.superuser)
        self.assertFalse(process_request_form.is_all_field_visible_to_admin_or_user_only())

    # -------------------
    # limit field
    # -------------------
    def test_get_limit_field_no_default_in_ansible_controller_no_override_in_squest(self):
        process_request_form = ProcessRequestForm(request=self.test_request, user=self.superuser)
        expected_initial = ""
        self.assertEqual(expected_initial, process_request_form.fields["ask_limit_on_launch"].initial)

    def test_get_limit_field_default_limit_set_in_ansible_controller_no_override_squest(self):
        self.test_request.operation.job_template.remote_job_template_data["limit"] = "test_limit"
        self.test_request.operation.job_template.save()
        process_request_form = ProcessRequestForm(request=self.test_request, user=self.superuser)
        expected_initial = "test_limit"
        self.assertEqual(expected_initial, process_request_form.fields["ask_limit_on_launch"].initial)

    def test_no_default_limit_set_in_ansible_controller_override_in_squest(self):
        self.test_request.operation.default_limits = "override_limit"
        self.test_request.operation.save()
        process_request_form = ProcessRequestForm(request=self.test_request, user=self.superuser)
        expected_initial = "override_limit"
        self.assertEqual(expected_initial, process_request_form.fields["ask_limit_on_launch"].initial)

    def test_default_limit_set_in_ansible_controller_override_in_squest(self):
        self.test_request.operation.job_template.remote_job_template_data["limit"] = "test_limit"
        self.test_request.operation.job_template.save()
        self.test_request.operation.default_limits = "override_limit"
        self.test_request.operation.save()
        process_request_form = ProcessRequestForm(request=self.test_request, user=self.superuser)
        expected_initial = "override_limit"
        self.assertEqual(expected_initial, process_request_form.fields["ask_limit_on_launch"].initial)

    # -------------------
    # inventory field
    # -------------------
    def test_get_inventory_field_default_in_ansible_controller_no_override_in_squest(self):
        process_request_form = ProcessRequestForm(request=self.test_request, user=self.superuser)
        expected_initial = 1
        self.assertEqual(expected_initial, process_request_form.fields["ask_inventory_on_launch"].initial)

    def test_get_inventory_field_default_in_ansible_controller_override_in_squest(self):
        self.test_request.operation.default_inventory_id = "3"
        self.test_request.operation.save()
        process_request_form = ProcessRequestForm(request=self.test_request, user=self.superuser)
        expected_initial = "3"
        self.assertEqual(expected_initial, process_request_form.fields["ask_inventory_on_launch"].initial)

    # -------------------
    # credentials field
    # -------------------
    def test_get_credentials_field_default_in_ansible_controller_no_override_in_squest(self):
        process_request_form = ProcessRequestForm(request=self.test_request, user=self.superuser)
        expected_initial = ['1']
        self.assertEqual(expected_initial, process_request_form.fields["ask_credential_on_launch"].initial)

    def test_get_credentials_field_default_in_ansible_controller_override_in_squest(self):
        # single value
        self.test_request.operation.default_credentials_ids = "2"
        self.test_request.operation.save()
        process_request_form = ProcessRequestForm(request=self.test_request, user=self.superuser)
        expected_initial = ['2']
        self.assertEqual(expected_initial, process_request_form.fields["ask_credential_on_launch"].initial)

        # comma separated list
        self.test_request.operation.default_credentials_ids = "2,3"
        self.test_request.operation.save()
        process_request_form = ProcessRequestForm(request=self.test_request, user=self.superuser)
        expected_initial = ['2', '3']
        self.assertEqual(expected_initial, process_request_form.fields["ask_credential_on_launch"].initial)
