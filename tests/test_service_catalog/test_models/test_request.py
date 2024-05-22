import json
from datetime import timedelta
from unittest import mock
from unittest.mock import Mock

import requests
import towerlib
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from django_fsm import can_proceed

from profiles.api.serializers import ScopeSerializerNested
from profiles.api.serializers.user_serializers import UserSerializerNested
from service_catalog.models import ApprovalWorkflow, ApprovalStep, ApprovalWorkflowState, ApprovalStepState
from service_catalog.models.instance import InstanceState, Instance
from service_catalog.models.request import RequestState, Request
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestRequest(BaseTestRequest):

    def setUp(self):
        super(TestRequest, self).setUp()
        self.test_request.state = RequestState.ACCEPTED
        self.test_request.save()
        self.expected_created_periodic_task_name = 'job_status_check_request_{}'.format(self.test_request.id)

    def _check_instance_state_after_process(self, expected_state):
        with mock.patch("service_catalog.models.job_templates.JobTemplate.execute") as mock_job_execute:
            mock_job_execute.return_value = 10, ""
            self.test_request.process()
            self.test_request.save()
            self.test_request.refresh_from_db()
            self.assertEqual(self.test_request.state, RequestState.PROCESSING)
            self.test_request.perform_processing()
            self.assertTrue(PeriodicTask.objects.filter(name=self.expected_created_periodic_task_name).exists())
            expected_extra_vars = {
                'text_variable': 'my_var',
            }
            expected_request = {
                'id': self.test_request.id,
                'state': RequestState.PROCESSING,
                'operation': self.test_request.operation.id,
                'user': UserSerializerNested(self.test_request.user).data
            }
            expected_instance = {
                'id': self.test_instance.id,
                'name': 'test_instance_1',
                'spec': {},
                'state': expected_state,
                'service': self.test_request.operation.service.id,
                'quota_scope': ScopeSerializerNested(self.test_quota_scope_org).data,
                'requester': UserSerializerNested(self.test_request.instance.requester).data
            }
            expected_user = UserSerializerNested(self.test_request.user).data
            mock_job_execute.assert_called()
            kwargs = mock_job_execute.call_args[1]
            expected_data_list = [expected_extra_vars, expected_request, expected_instance, expected_user]
            data_list = [
                kwargs.get("extra_vars", None),
                kwargs.get("extra_vars", None).get('squest', None).get('request', None),
                kwargs.get("extra_vars", None).get('squest', None).get('request', None).get('instance', None),
                kwargs.get("extra_vars", None).get('squest', None).get('request', None).get('user', None)
            ]
            for expected_data, data in zip(expected_data_list, data_list):
                for key_var, val_var in expected_data.items():
                    self.assertIn(key_var, data.keys())
                    self.assertEqual(val_var, data[key_var])
            self.test_instance.refresh_from_db()
            self.assertEqual(self.test_instance.state, expected_state)

    def test_process_pending_instance_to_be_provisioned(self):
        expected_state = InstanceState.PROVISIONING
        self._check_instance_state_after_process(expected_state)

    def test_process_available_instance_to_be_updated(self):
        self.test_instance.state = InstanceState.AVAILABLE
        self.test_instance.save()
        self.test_request.operation = self.update_operation_test
        self.test_request.save()
        expected_state = InstanceState.UPDATING
        self._check_instance_state_after_process(expected_state)

    def test_process_available_instance_to_be_deleted(self):
        self.test_instance.state = InstanceState.AVAILABLE
        self.test_instance.save()
        self.test_request.operation = self.delete_operation_test
        self.test_request.save()
        expected_state = InstanceState.DELETING
        self._check_instance_state_after_process(expected_state)

    def _process_with_job_template_execution_failure(self, expected_instance_state, side_effect=None):
        if side_effect is None:
            side_effect = requests.exceptions.ConnectionError('Test')
        with mock.patch("service_catalog.models.job_templates.JobTemplate.execute") as mock_job_execute:
            mock_job_execute.side_effect = Mock(side_effect=side_effect)
            self.test_request.process()
            self.test_request.perform_processing()
            self.test_instance.refresh_from_db()
            self.assertEqual(self.test_instance.state, expected_instance_state)
            self.assertEqual(self.test_request.state, RequestState.FAILED)
            self.assertIsNotNone(self.test_request.failure_message)
            mock_job_execute.assert_called()

    def test_failure_when_provisioning(self):
        expected_instance_state = InstanceState.PROVISION_FAILED
        self._process_with_job_template_execution_failure(expected_instance_state)

    def test_ssl_failure_when_provisioning(self):
        expected_instance_state = InstanceState.PROVISION_FAILED
        self._process_with_job_template_execution_failure(expected_instance_state,
                                                          side_effect=requests.exceptions.SSLError('Test'))

    def test_auth_failure_when_provisioning(self):
        expected_instance_state = InstanceState.PROVISION_FAILED
        self._process_with_job_template_execution_failure(expected_instance_state,
                                                          side_effect=towerlib.towerlibexceptions.AuthFailed('Test'))

    def test_failure_when_updating(self):
        self.test_instance.state = InstanceState.AVAILABLE
        self.test_instance.save()
        self.test_request.operation = self.update_operation_test
        self.test_request.save()
        expected_instance_state = InstanceState.UPDATE_FAILED
        self._process_with_job_template_execution_failure(expected_instance_state)

    def test_failure_when_deleting(self):
        self.test_instance.state = InstanceState.AVAILABLE
        self.test_instance.save()
        self.test_request.operation = self.delete_operation_test
        self.test_request.save()
        expected_instance_state = InstanceState.DELETE_FAILED
        self._process_with_job_template_execution_failure(expected_instance_state)

    def _check_request_after_create(self, expected_state, check_execution_called):
        form_data = {'name': 'test instance', 'text_variable': 'my_var'}

        with mock.patch("service_catalog.models.job_templates.JobTemplate.execute") as mock_job_execute:
            mock_job_execute.return_value = 10, ""
            new_request = Request.objects.create(fill_in_survey=form_data,
                                                 instance=self.test_instance,
                                                 operation=self.create_operation_test,
                                                 user=self.standard_user)
            new_request.refresh_from_db()
            self.assertEqual(new_request.state, expected_state)
            if check_execution_called:
                mock_job_execute.assert_called()

    def _check_state_after_accept(self, expected_instance_state, expected_request_state):
        with mock.patch("service_catalog.models.job_templates.JobTemplate.execute") as mock_job_execute:
            mock_job_execute.return_value = 10, ""
            self.test_request.accept(self.superuser)
            self.test_request.refresh_from_db()
            self.assertEqual(self.test_instance.state, expected_instance_state)
            self.assertEqual(self.test_request.state, expected_request_state)
            if expected_request_state == RequestState.PROCESSING:
                self.assertTrue(PeriodicTask.objects.filter(name=self.expected_created_periodic_task_name).exists())
                expected_extra_vars = {
                    'text_variable': 'my_var',
                }
                expected_request = {
                    'id': self.test_request.id,
                    'state': RequestState.PROCESSING,
                    'operation': self.test_request.operation.id,
                    'user': UserSerializerNested(self.test_request.user).data
                }
                expected_instance = {
                    'id': self.test_instance.id,
                    'name': 'test_instance_1',
                    'spec': {},
                    'state': expected_instance_state,
                    'service': self.test_request.operation.service.id,
                    'quota_scope': ScopeSerializerNested(self.test_quota_scope_org).data,
                    'requester': UserSerializerNested(self.test_request.instance.requester).data
                }
                expected_user = UserSerializerNested(self.test_request.user).data
                mock_job_execute.assert_called()
                kwargs = mock_job_execute.call_args[1]
                expected_data_list = [expected_extra_vars, expected_request, expected_instance, expected_user]
                data_list = [
                    kwargs.get("extra_vars", None),
                    kwargs.get("extra_vars", None).get('squest', None).get('request', None),
                    kwargs.get("extra_vars", None).get('squest', None).get('request', None).get('instance', None),
                    kwargs.get("extra_vars", None).get('squest', None).get('request', None).get('user', None)
                ]
                for expected_data, data in zip(expected_data_list, data_list):
                    for key_var, val_var in expected_data.items():
                        self.assertIn(key_var, data.keys())
                        self.assertEqual(val_var, data[key_var])

    def test_request_accepted_automatically(self):
        self.create_operation_test.auto_accept = True
        self.create_operation_test.save()
        self._check_request_after_create(RequestState.ACCEPTED, check_execution_called=False)

    def test_request_processing_automatically(self):
        self.create_operation_test.auto_accept = True
        self.create_operation_test.auto_process = True
        self.create_operation_test.save()
        self._check_request_after_create(RequestState.PROCESSING, check_execution_called=True)

    def test_auto_accept_with_approval_step(self):
        self.test_approval_workflow = ApprovalWorkflow.objects.create(name="test_approval_workflow",
                                                                      operation=self.create_operation_test,
                                                                      enabled=True)
        auto_accept_condition = "request.instance.name == 'test_instance_1'"
        ApprovalStep.objects.create(name="test_approval_step_1",
                                    approval_workflow=self.test_approval_workflow,
                                    auto_accept_condition=auto_accept_condition)
        self._check_request_after_create(RequestState.ACCEPTED, check_execution_called=False)

    def test_auto_accept_with_2_approval_step(self):
        self.test_approval_workflow = ApprovalWorkflow.objects.create(name="test_approval_workflow",
                                                                      operation=self.create_operation_test,
                                                                      enabled=True)
        auto_accept_condition_1 = "request.instance.name == 'test_instance_1'"
        ApprovalStep.objects.create(name="test_approval_step_1",
                                    approval_workflow=self.test_approval_workflow,
                                    auto_accept_condition=auto_accept_condition_1)
        auto_accept_condition_2 = "request.fill_in_survey['text_variable'] == 'my_var'"
        ApprovalStep.objects.create(name="test_approval_step_2",
                                    approval_workflow=self.test_approval_workflow,
                                    auto_accept_condition=auto_accept_condition_2)
        self._check_request_after_create(RequestState.ACCEPTED, check_execution_called=False)

    def test_request_not_processing_automatically_if_auto_accept_false(self):
        self.create_operation_test.auto_accept = False
        self.create_operation_test.auto_process = True
        self.create_operation_test.save()
        self._check_request_after_create(RequestState.SUBMITTED, check_execution_called=False)
        self._check_state_after_accept(InstanceState.PROVISIONING, RequestState.PROCESSING)

    def _process_timeout_with_expected_state(self, expected_instance_state):
        self.test_request.state = RequestState.PROCESSING
        self.test_request.tower_job_id = 10
        date_in_the_past = timezone.now() - timedelta(seconds=45)
        self.test_request.periodic_task_date_expire = date_in_the_past
        schedule, created = IntervalSchedule.objects.get_or_create(every=10,
                                                                   period=IntervalSchedule.SECONDS)
        self.test_request.periodic_task = PeriodicTask.objects.create(
            interval=schedule,
            name='job_status_check_request_{}'.format(self.test_request.id),
            task='service_catalog.tasks.check_tower_job_status_task',
            args=json.dumps([self.test_request.id]))
        self.test_request.save()

        with mock.patch("django_celery_beat.models.PeriodicTask.delete") as mock_periodic_task_delete:
            self.test_request.check_job_status()
            self.test_instance.refresh_from_db()
            self.test_request.refresh_from_db()
            self.assertEqual(self.test_instance.state, expected_instance_state)
            self.assertEqual(self.test_request.state, RequestState.FAILED)
            mock_periodic_task_delete.assert_called()

    def test_job_id_none_when_executing(self):
        with mock.patch("service_catalog.models.job_templates.JobTemplate.execute") as mock_job_execute:
            mock_job_execute.return_value = None, "error"
            self.test_request.process()
            self.test_request.perform_processing()
            self.test_request.refresh_from_db()
            self.test_instance.refresh_from_db()
            self.assertEqual(self.test_request.state, RequestState.FAILED)
            self.assertEqual(self.test_request.failure_message, "error")
            self.assertEqual(self.test_instance.state, InstanceState.PROVISION_FAILED)

    def test_process_timeout_when_provisioning(self):
        self.test_instance.state = InstanceState.PROVISIONING
        self.test_instance.save()
        expected_instance_state = InstanceState.PROVISION_FAILED
        self._process_timeout_with_expected_state(expected_instance_state)

    def test_process_timeout_when_updating(self):
        self.test_instance.state = InstanceState.UPDATING
        self.test_instance.save()
        self.test_request.operation = self.update_operation_test
        self.test_request.save()
        expected_instance_state = InstanceState.UPDATE_FAILED
        self._process_timeout_with_expected_state(expected_instance_state)

    def test_process_timeout_when_deleting(self):
        self.test_instance.state = InstanceState.DELETING
        self.test_instance.save()
        self.test_request.operation = self.delete_operation_test
        self.test_request.save()
        expected_instance_state = InstanceState.DELETE_FAILED
        self._process_timeout_with_expected_state(expected_instance_state)

    def test_tower_job_url(self):
        self.test_request.tower_job_id = 1234
        self.assertEqual("https://localhost/#/jobs/playbook/1234/output", self.test_request.tower_job_url)

    def test_delete_request_also_delete_periodic_task(self):
        crontab = CrontabSchedule.objects.create(minute=0, hour=5)
        periodic_task_test = PeriodicTask.objects.create(name="test-periodic-request", crontab=crontab)
        self.assertTrue(PeriodicTask.objects.filter(id=periodic_task_test.id).exists())
        self.test_request.periodic_task = periodic_task_test
        self.test_request.save()
        self.test_request.delete()
        self.assertFalse(PeriodicTask.objects.filter(id=periodic_task_test.id).exists())

    def test_check_job_status_when_no_tower_job_id_set(self):
        self.assertIsNone(self.test_request.check_job_status())

    def _prepare_base_request_for_test(self):
        self.test_request.tower_job_id = 123
        self.test_instance.save()
        self.test_request.periodic_task_date_expire = timezone.now() + timezone.timedelta(days=1)
        crontab = CrontabSchedule.objects.create(minute=0, hour=5)
        self.periodic_task_test = PeriodicTask.objects.create(name="test-periodic-request", crontab=crontab)
        self.assertTrue(PeriodicTask.objects.filter(id=self.periodic_task_test.id).exists())
        self.test_request.periodic_task = self.periodic_task_test
        self.test_request.save()

    def _check_request_complete(self, expected_instance_state):
        self.test_request.state = RequestState.PROCESSING
        self.test_request.save()
        with mock.patch("service_catalog.models.tower_server.TowerServer.get_tower_instance") as tower_mock:
            tower_mock.return_value.get_unified_job_by_id.return_value.status = "successful"
            with mock.patch("service_catalog.mail_utils.send_mail_request_update") as mock_email:
                self.test_request.check_job_status()
                self.test_request.refresh_from_db()
                mock_email.assert_called()
                self.assertEqual(self.test_request.state, RequestState.COMPLETE)
                self.assertFalse(PeriodicTask.objects.filter(id=self.periodic_task_test.id).exists())
                self.assertEqual(self.test_instance.state, expected_instance_state)

    def test_check_job_status_successful_operation_create(self):
        self._prepare_base_request_for_test()
        self.test_instance.state = InstanceState.PROVISIONING
        self.test_instance.save()
        self.assertIsNone(self.test_request.instance.date_available)
        self._check_request_complete(expected_instance_state=InstanceState.AVAILABLE)
        self.assertIsNotNone(self.test_request.instance.date_available)

    def test_check_job_status_successful_operation_update(self):
        self._prepare_base_request_for_test()
        self.test_instance.state = InstanceState.UPDATING
        self.test_instance.save()
        self.test_request.operation = self.update_operation_test
        self._check_request_complete(expected_instance_state=InstanceState.AVAILABLE)

    def test_check_job_status_successful_operation_delete(self):
        self._prepare_base_request_for_test()
        self.test_instance.state = InstanceState.DELETING
        self.test_instance.save()
        self.test_request.operation = self.delete_operation_test
        self._check_request_complete(expected_instance_state=InstanceState.DELETED)

    def _test_request_fail(self, job_status):
        self._prepare_base_request_for_test()
        self.test_request.state = RequestState.PROCESSING
        self.test_request.save()
        self.test_instance.state = InstanceState.PROVISIONING
        self.test_instance.save()
        with mock.patch("service_catalog.models.tower_server.TowerServer.get_tower_instance") as tower_mock:
            tower_mock.return_value.get_unified_job_by_id.return_value.status = job_status
            with mock.patch("service_catalog.mail_utils.send_mail_request_update") as mock_email:
                self.test_request.check_job_status()
                self.test_request.refresh_from_db()
                mock_email.assert_called()
                self.assertEqual(self.test_request.state, RequestState.FAILED)
                self.assertFalse(PeriodicTask.objects.filter(id=self.periodic_task_test.id).exists())
                self.assertEqual(self.test_instance.state, InstanceState.PROVISION_FAILED)

    def test_check_job_status_cancel(self):
        self._test_request_fail(job_status="canceled")

    def test_check_job_status_failed(self):
        self._test_request_fail(job_status="failed")

    def test_cancel(self):
        self.assertTrue(Instance.objects.filter(id=self.test_instance.id).exists())
        self.test_request.cancel()
        self.assertEqual(self.test_request.instance.state, InstanceState.ABORTED)

    def test_reprocess_after_failed(self):
        for state in [InstanceState.PENDING, InstanceState.PROVISION_FAILED, InstanceState.AVAILABLE,
                      InstanceState.DELETE_FAILED, InstanceState.UPDATE_FAILED]:
            self.test_request.state = RequestState.FAILED
            self.test_request.save()
            self.test_request.instance.state = state
            self.test_request.instance.save()
            self.assertTrue(can_proceed(self.test_request.process))

    def test_get_full_survey(self):
        # end user survey
        self.test_request.fill_in_survey = {
            'text_variable': "myvar"
        }
        self.test_request.save()
        self.assertEqual(self.test_request.full_survey['text_variable'], "myvar")

        # add a step on the opereration
        self.test_approval_workflow = ApprovalWorkflow.objects.create(name="test_approval_workflow",
                                                                      operation=self.create_operation_test,
                                                                      enabled=True)
        self.test_approval_workflow_state = ApprovalWorkflowState.objects.create(approval_workflow=self.test_approval_workflow)
        self.test_request.approval_workflow_state = self.test_approval_workflow_state
        self.test_request.save()
        self.test_approval_step_1 = ApprovalStep.objects.create(name="test_approval_step_1",
                                                                approval_workflow=self.test_approval_workflow)
        self.test_approval_step_state_1 = ApprovalStepState.objects.create(
            approval_workflow_state=self.test_approval_workflow_state,
            approval_step=self.test_approval_step_1)
        self.test_approval_step_state_1.fill_in_survey = {
            'text_variable': "updated_by_step"
        }
        self.test_approval_step_state_1.save()
        self.assertEqual(self.test_request.full_survey['text_variable'], "updated_by_step")

        # Admin replace a value
        self.test_request.admin_fill_in_survey = {
            'text_variable': "updated_by_admin"
        }
        self.test_request.save()
        self.assertEqual(self.test_request.full_survey['text_variable'], "updated_by_admin")

    def test_update_fill_in_surveys_accept_request(self):
        new_survey_config = {
            'text_variable': True,
            'textarea_var': True,
            'multiplechoice_variable': False,
            'multiselect_var': False,
            'password_var': False,
            'float_var': False,
            'integer_var': False
        }
        self.test_request.operation.switch_tower_fields_enable_from_dict(new_survey_config)
        self.test_request.fill_in_survey = {
            'text_variable': "value",
            'textarea_var': "textarea_value",
        }
        self.test_request.admin_fill_in_survey = {
            'multiplechoice_variable': "choice1",
            'multiselect_var': [],
            'password_var': "password_val",
            'float_var': 0,
            'integer_var': 12
        }
        self.test_request.save()

        admin_accept_survey = {
            'text_variable': "value_updated",
            'textarea_var': "textarea_value_updated",
            'multiplechoice_variable': "choice1",
            'multiselect_var': [],
            'password_var': "password_val_updated",
            'float_var': 1,
            'integer_var': 14
        }

        self.test_request.update_fill_in_surveys_accept_request(admin_accept_survey)
        self.test_request.refresh_from_db()

        expected_fill_in_survey = {
            'text_variable': "value_updated",
            'textarea_var': "textarea_value_updated",
        }

        expected_admin_fill_in_survey = {
            'multiplechoice_variable': "choice1",
            'multiselect_var': [],
            'password_var': "password_val_updated",
            'float_var': 1,
            'integer_var': 14
        }
        self.assertDictEqual(self.test_request.fill_in_survey, expected_fill_in_survey)
        self.assertDictEqual(self.test_request.admin_fill_in_survey, expected_admin_fill_in_survey)

    def test_request_extra_vars(self):
        self.test_request.process()
        self.test_request.save()

        # add extra vars on tower server
        self.tower_server_test.extra_vars = {
            "tower_server_extra_var_key1": "tower_server_extra_var_value1",
            "tower_server_extra_var_key2": "tower_server_extra_var_value2"
        }
        self.service_test.extra_vars = {
            "service_extra_var_key1": "service_extra_var_value1",
            "service_extra_var_key2": "service_extra_var_value2"
        }
        self.create_operation_test.extra_vars = {
            "operation_extra_var_key": "operation_extra_var_value"
        }
        with mock.patch("service_catalog.models.job_templates.JobTemplate.execute") as mock_job_execute:
            mock_job_execute.return_value = 10, ""
            self.test_request.perform_processing()
            args, executed_extra_vars = mock_job_execute.call_args
            self.assertEqual(executed_extra_vars["extra_vars"]["tower_server_extra_var_key1"],
                             "tower_server_extra_var_value1")
            self.assertEqual(executed_extra_vars["extra_vars"]["tower_server_extra_var_key2"],
                             "tower_server_extra_var_value2")
            self.assertEqual(executed_extra_vars["extra_vars"]["service_extra_var_key1"], "service_extra_var_value1")
            self.assertEqual(executed_extra_vars["extra_vars"]["service_extra_var_key2"], "service_extra_var_value2")
            self.assertEqual(executed_extra_vars["extra_vars"]["operation_extra_var_key"], "operation_extra_var_value")
            mock_job_execute.assert_called()

    def test_service_extra_vars(self):
        self.test_request.process()
        self.test_request.save()
        self.service_test.extra_vars = {
            "tower_server_extra_var_key1": "tower_server_extra_var_overridden_by_service1",
            "tower_server_extra_var_key2": "tower_server_extra_var_overridden_by_service2"
        }
        with mock.patch("service_catalog.models.job_templates.JobTemplate.execute") as mock_job_execute:
            mock_job_execute.return_value = 10, ""
            self.test_request.perform_processing()
            args, executed_extra_vars = mock_job_execute.call_args
            self.assertEqual(executed_extra_vars["extra_vars"]["tower_server_extra_var_key1"],
                             "tower_server_extra_var_overridden_by_service1")
            self.assertEqual(executed_extra_vars["extra_vars"]["tower_server_extra_var_key2"],
                             "tower_server_extra_var_overridden_by_service2")

    def test_operation_extra_vars(self):
        self.test_request.process()
        self.test_request.save()
        self.service_test.extra_vars = {
            "tower_server_extra_var_key1": "tower_server_extra_var_overridden_by_service1",
            "tower_server_extra_var_key2": "tower_server_extra_var_overridden_by_service2"
        }
        self.create_operation_test.extra_vars = {
            "tower_server_extra_var_key1": "tower_server_extra_var_overridden_by_operation"
        }
        with mock.patch("service_catalog.models.job_templates.JobTemplate.execute") as mock_job_execute:
            mock_job_execute.return_value = 10, ""
            self.test_request.perform_processing()
            args, executed_extra_vars = mock_job_execute.call_args
            self.assertEqual(executed_extra_vars["extra_vars"]["tower_server_extra_var_key1"],
                             "tower_server_extra_var_overridden_by_operation")
            self.assertEqual(executed_extra_vars["extra_vars"]["tower_server_extra_var_key2"],
                             "tower_server_extra_var_overridden_by_service2")

    def test_date_submitted_not_update_on_save(self):
        new_request = Request.objects.create(fill_in_survey={}, instance=self.test_instance,
                                             operation=self.create_operation_test, user=self.standard_user)
        old_submitted_date = new_request.date_submitted
        new_request.save()
        self.assertEqual(old_submitted_date, new_request.date_submitted)
