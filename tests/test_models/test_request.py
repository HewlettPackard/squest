from unittest import mock
from unittest.mock import Mock

import requests
from django_celery_beat.models import PeriodicTask

from service_catalog.models.instance import InstanceState
from service_catalog.models.request import RequestState, Request
from tests.base_test_request import BaseTestRequest


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
            self.assertEquals(self.test_request.state, RequestState.PROCESSING)
            self.test_request.perform_processing()
            self.assertTrue(PeriodicTask.objects.filter(name=self.expected_created_periodic_task_name).exists())
            expected_extra_vars = {
                'instance_name': 'test instance',
                'text_variable': 'my_var',
                'tsc': {
                    'instance': {
                        'id': self.test_instance.id,
                        'name': 'test_instance_1',
                        'spec': {},
                        'state': str(expected_state),
                        'service': self.test_request.operation.service.id
                    }
                }
            }
            mock_job_execute.assert_called_with(extra_vars=expected_extra_vars)
            self.test_instance.refresh_from_db()
            self.assertEquals(self.test_instance.state, expected_state)

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

    def _process_with_job_template_execution_failure(self, expected_instance_state):
        side_effect = requests.exceptions.ConnectionError('Test')
        with mock.patch("service_catalog.models.job_templates.JobTemplate.execute") as mock_job_execute:
            mock_job_execute.side_effect = Mock(side_effect=side_effect)
            self.test_request.process()
            self.test_request.perform_processing()
            self.test_instance.refresh_from_db()
            self.assertEquals(self.test_instance.state, expected_instance_state)
            self.assertEquals(self.test_request.state, RequestState.FAILED)
            mock_job_execute.assert_called()

    def test_failure_when_provisioning(self):
        expected_instance_state = InstanceState.PROVISION_FAILED
        self._process_with_job_template_execution_failure(expected_instance_state)

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
            self.assertEquals(new_request.state, expected_state)
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
