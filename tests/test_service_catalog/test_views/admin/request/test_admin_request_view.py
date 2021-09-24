from unittest import mock

from django.urls import reverse

from service_catalog.models import Request, RequestMessage, ExceptionServiceCatalog
from service_catalog.models.instance import InstanceState
from service_catalog.models.request import RequestState
from tests.test_service_catalog.base_test_request import BaseTestRequest


class CustomerRequestViewTest(BaseTestRequest):

    def setUp(self):
        super(CustomerRequestViewTest, self).setUp()

    def test_admin_request_cancel(self):
        args = {
            'request_id': self.test_request.id
        }
        url = reverse('service_catalog:admin_request_cancel', kwargs=args)
        response = self.client.post(url)
        self.assertEquals(302, response.status_code)
        self.assertEquals(0, Request.objects.filter(id=self.test_request.id).count())

    def test_admin_request_need_info(self):
        args = {
            'request_id': self.test_request.id
        }
        url = reverse('service_catalog:admin_request_need_info', kwargs=args)
        data = {
            "message": "admin message"
        }
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.test_request.refresh_from_db()
        self.assertEquals(self.test_request.state, RequestState.NEED_INFO)
        self.assertEquals(1, RequestMessage.objects.filter(request=self.test_request.id).count())

    def test_admin_request_re_submit(self):
        self.test_request.state = RequestState.NEED_INFO
        self.test_request.save()
        args = {
            'request_id': self.test_request.id
        }
        url = reverse('service_catalog:admin_request_re_submit', kwargs=args)
        response = self.client.post(url)
        self.assertEquals(302, response.status_code)
        self.test_request.refresh_from_db()
        self.assertEquals(self.test_request.state, RequestState.SUBMITTED)

    def test_admin_request_reject(self):
        args = {
            'request_id': self.test_request.id
        }
        url = reverse('service_catalog:admin_request_reject', kwargs=args)
        data = {
            "message": "admin message"
        }
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.test_request.refresh_from_db()
        self.assertEquals(self.test_request.state, RequestState.REJECTED)
        self.assertEquals(1, RequestMessage.objects.filter(request=self.test_request.id).count())

    def _accept_request_with_expected_state(self, expected_request_state, expected_instance_state, custom_data=None):
        args = {
            'request_id': self.test_request.id
        }
        if custom_data:
            data = custom_data
        else:
            data = {'text_variable': 'my_var',
                    'multiplechoice_variable': 'choice1',
                    'multiselect_var': 'multiselect_1',
                    'textarea_var': '2',
                    'password_var': 'pass',
                    'integer_var': '1',
                    'float_var': '0.6'
                    }

        url = reverse('service_catalog:admin_request_accept', kwargs=args)
        response = self.client.post(url, data=data)
        self.assertEquals(302, response.status_code)
        self.test_request.refresh_from_db()
        self.assertEquals(self.test_request.state, expected_request_state)
        self.test_instance.refresh_from_db()
        self.assertEquals(self.test_instance.state, expected_instance_state)

    def test_admin_request_accept_pending_instance(self):
        self._accept_request_with_expected_state(expected_request_state=RequestState.ACCEPTED,
                                                 expected_instance_state=InstanceState.PENDING)

    def test_admin_request_accept_accepted_instance(self):
        self._accept_request_with_expected_state(expected_request_state=RequestState.ACCEPTED,
                                                 expected_instance_state=InstanceState.PENDING)
        self.test_request.refresh_from_db()
        old_survey = self.test_request.fill_in_survey
        data = {
            'text_variable': 'var',
            'multiplechoice_variable': 'choice1',
            'multiselect_var': 'multiselect_1',
            'textarea_var': '1',
            'password_var': 'password',
            'integer_var': '2',
            'float_var': '0.8'
        }
        self._accept_request_with_expected_state(expected_request_state=RequestState.ACCEPTED,
                                                 expected_instance_state=InstanceState.PENDING, custom_data=data)
        self.test_request.refresh_from_db()
        data_expected = {
            'text_variable': 'var',
            'multiplechoice_variable': 'choice1',
            'multiselect_var': ['multiselect_1'],
            'textarea_var': '1',
            'password_var': 'password',
            'integer_var': 2,
            'float_var': 0.8
        }
        self.assertDictEqual(self.test_request.fill_in_survey, data_expected)
        self.assertNotEqual(self.test_request.fill_in_survey, old_survey)

    def test_admin_request_accept_failed_update(self):
        self.test_instance.state = InstanceState.UPDATE_FAILED
        self.test_instance.save()
        self.test_request.state = RequestState.FAILED
        self.test_request.save()
        self._accept_request_with_expected_state(expected_request_state=RequestState.ACCEPTED,
                                                 expected_instance_state=InstanceState.AVAILABLE)

    def test_admin_request_accept_failed_provisioning(self):
        self.test_instance.state = InstanceState.PROVISION_FAILED
        self.test_instance.save()
        self.test_request.state = RequestState.FAILED
        self.test_request.save()
        self._accept_request_with_expected_state(expected_request_state=RequestState.ACCEPTED,
                                                 expected_instance_state=InstanceState.PENDING)

    def test_admin_request_accept_failed_delete(self):
        self.test_instance.state = InstanceState.DELETE_FAILED
        self.test_instance.save()
        self.test_request.state = RequestState.FAILED
        self.test_request.save()
        self._accept_request_with_expected_state(expected_request_state=RequestState.ACCEPTED,
                                                 expected_instance_state=InstanceState.AVAILABLE)

    def _process_with_expected_instance_state(self, expected_instance_state,
                                              expected_request_state=RequestState.PROCESSING, mock_value=None):
        if mock_value is None:
            mock_value = 10
        args = {
            'request_id': self.test_request.id
        }
        url = reverse('service_catalog:admin_request_process', kwargs=args)
        with mock.patch("service_catalog.models.job_templates.JobTemplate.execute") as mock_job_execute:
            if isinstance(mock_value, Exception):
                mock_job_execute.side_effect = mock_value
            else:
                mock_job_execute.return_value = mock_value
            response = self.client.post(url)
            self.assertEquals(302, response.status_code)
            self.test_request.refresh_from_db()
            self.assertEquals(self.test_request.state, expected_request_state)
            expected_parameters = {
                'instance_name': 'test instance',
                'text_variable': 'my_var',
                'squest': {
                    'request': {
                        'id': self.test_request.id,
                        'state': RequestState.PROCESSING,
                        'operation': self.test_request.operation.id,
                        'instance': {
                            'id': self.test_instance.id,
                            'name': 'test_instance_1',
                            'spec': {},
                            'state': str(expected_instance_state),
                            'service': self.test_request.operation.service.id,
                            'billing_group': None,
                            'spoc': self.test_request.instance.spoc.id
                        }
                    }
                }
            }
            self.test_instance.refresh_from_db()
            self.assertEquals(self.test_instance.state, expected_instance_state)
            if not isinstance(mock_value, Exception):
                self.assertIsNotNone(self.test_request.periodic_task)
                mock_job_execute.assert_called_with(extra_vars=expected_parameters)

    def test_admin_request_process_new_instance(self):
        self.test_request.state = RequestState.ACCEPTED
        self.test_request.save()
        self._process_with_expected_instance_state(InstanceState.PROVISIONING)

    def test_admin_request_process_update_instance(self):
        self.test_instance.state = InstanceState.AVAILABLE
        self.test_instance.save()
        self.test_request.state = RequestState.ACCEPTED
        self.test_request.operation = self.update_operation_test
        self.test_request.save()
        self._process_with_expected_instance_state(InstanceState.UPDATING)

    def test_admin_request_process_delete_instance(self):
        self.test_instance.state = InstanceState.AVAILABLE
        self.test_instance.save()
        self.test_request.state = RequestState.ACCEPTED
        self.test_request.operation = self.delete_operation_test
        self.test_request.save()
        self._process_with_expected_instance_state(InstanceState.DELETING)

    def test_cannot_process_if_another_request_process_already(self):
        self.test_instance.state = InstanceState.UPDATING
        self.test_instance.save()
        self.test_request.state = RequestState.PROCESSING
        self.test_request.operation = self.update_operation_test
        self.test_request.save()

        # second request
        request_update = Request.objects.create(fill_in_survey={},
                                                instance=self.test_instance,
                                                operation=self.update_operation_test)
        request_update.state = RequestState.ACCEPTED
        request_update.save()
        args = {
            'request_id': request_update.id
        }
        url = reverse('service_catalog:admin_request_process', kwargs=args)
        response = self.client.post(url)
        self.assertEquals(403, response.status_code)

    def test_admin_request_process_new_instance_on_non_exist_job_template_id(self):
        self.test_request.state = RequestState.ACCEPTED
        self.test_request.save()
        self._process_with_expected_instance_state(InstanceState.PROVISION_FAILED, RequestState.FAILED,
                                                   ExceptionServiceCatalog.JobTemplateNotFound(
                                                       tower_name=self.tower_server_test.name,
                                                       job_template_id=self.job_template_test.tower_id))
        self.test_request.refresh_from_db()
        self.assertIsNotNone(self.test_request.failure_message)

    def test_admin_request_details(self):
        args = {
            'request_id': self.test_request.id
        }
        url = reverse('service_catalog:admin_request_details', kwargs=args)
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)

    def _validate_access_request_details(self):
        args = {
            'request_id': self.test_request.id
        }
        url = reverse('service_catalog:admin_request_details', kwargs=args)
        response = self.client.get(url)
        self.assertEquals(302, response.status_code)

    def test_customer_cannot_access_request_details(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        self._validate_access_request_details()

    def test_not_logged_cannot_access_request_details(self):
        self.client.logout()
        self._validate_access_request_details()
