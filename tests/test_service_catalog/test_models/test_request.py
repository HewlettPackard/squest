import json
from datetime import timedelta
from unittest import mock
from unittest.mock import Mock

import requests
import towerlib
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from django_fsm import can_proceed

from profiles.api.serializers.user_serializers import UserSerializer
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
            mock_job_execute.return_value = 10
            self.test_request.process()
            self.test_request.save()
            self.test_request.refresh_from_db()
            self.assertEqual(self.test_request.state, RequestState.PROCESSING)
            self.test_request.perform_processing()
            self.assertTrue(PeriodicTask.objects.filter(name=self.expected_created_periodic_task_name).exists())
            expected_extra_vars = {
                'instance_name': 'test instance',
                'text_variable': 'my_var',
            }
            expected_request = {
                'id': self.test_request.id,
                'state': RequestState.PROCESSING,
                'operation': self.test_request.operation.id,
                'user': UserSerializer(self.test_request.user).data
            }
            expected_instance = {
                'id': self.test_instance.id,
                'name': 'test_instance_1',
                'spec': {},
                'state': str(expected_state),
                'service': self.test_request.operation.service.id,
                'billing_group': None,
                'spoc': self.test_request.instance.spoc.id
            }
            expected_user = UserSerializer(self.test_request.user).data
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
        form_data = {'instance_name': 'test instance', 'text_variable': 'my_var'}

        with mock.patch("service_catalog.models.job_templates.JobTemplate.execute") as mock_job_execute:
            mock_job_execute.return_value = 10
            new_request = Request.objects.create(fill_in_survey=form_data,
                                                 instance=self.test_instance,
                                                 operation=self.create_operation_test,
                                                 user=self.standard_user)
            self.assertEqual(new_request.state, expected_state)
            if check_execution_called:
                mock_job_execute.assert_called()

    def test_request_accepted_automatically(self):
        self.create_operation_test.auto_accept = True
        self.create_operation_test.save()
        self._check_request_after_create(RequestState.ACCEPTED, check_execution_called=False)

    def test_request_processing_automatically(self):
        self.create_operation_test.auto_accept = True
        self.create_operation_test.auto_process = True
        self.create_operation_test.save()
        self._check_request_after_create(RequestState.PROCESSING, check_execution_called=True)

    def test_request_not_processing_automatically_if_auto_accept_false(self):
        self.create_operation_test.auto_accept = False
        self.create_operation_test.auto_process = True
        self.create_operation_test.save()
        self._check_request_after_create(RequestState.SUBMITTED, check_execution_called=False)

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
       self.assertEqual("https://localhost/#/jobs", self.test_request.tower_job_url)

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
        self.assertFalse(Instance.objects.filter(id=self.test_instance.id).exists())

    def test_reprocess_after_failed(self):
        for state in [InstanceState.PENDING, InstanceState.PROVISION_FAILED, InstanceState.AVAILABLE,
                      InstanceState.DELETE_FAILED, InstanceState.UPDATE_FAILED]:
            self.test_request.state = RequestState.FAILED
            self.test_request.save()
            self.test_request.instance.state = state
            self.test_request.instance.save()
            self.assertTrue(can_proceed(self.test_request.process))
