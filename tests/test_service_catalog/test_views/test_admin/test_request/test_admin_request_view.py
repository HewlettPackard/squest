from unittest import mock

from django.urls import reverse

from profiles.api.serializers import ScopeSerializer
from profiles.api.serializers.user_serializers import UserSerializer
from service_catalog.models import Request, RequestMessage, ExceptionServiceCatalog
from service_catalog.models.instance import InstanceState
from service_catalog.models.request import RequestState
from tests.test_service_catalog.base_test_request import BaseTestRequest


class AdminRequestViewTest(BaseTestRequest):

    def setUp(self):
        super(AdminRequestViewTest, self).setUp()
        self.test_request.admin_fill_in_survey = {
            'multiplechoice_variable': "choice1",
            'multiselect_var': ["multiselect_3", "multiselect_2"],
            'textarea_var': "textarea_val",
            'password_var': "password_val",
            'float_var': 1.5,
            'integer_var': 1
        }
        self.test_request.save()

    def test_request_cancel(self):
        args = {
            'pk': self.test_request.id
        }
        url = reverse('service_catalog:request_cancel', kwargs=args)
        response = self.client.post(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual(0, Request.objects.filter(id=self.test_request.id).count())

    def test_request_need_info(self):
        args = {
            'pk': self.test_request.id
        }
        url = reverse('service_catalog:request_need_info', kwargs=args)
        data = {
            "content": "admin message"
        }
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.test_request.refresh_from_db()
        self.assertEqual(self.test_request.state, RequestState.NEED_INFO)
        self.assertEqual(1, RequestMessage.objects.filter(request=self.test_request.id).count())

    def test_admin_cannot_request_need_info_on_forbidden_states(self):
        args = {
            'pk': self.test_request.id
        }
        url = reverse('service_catalog:request_need_info', kwargs=args)
        data = {
            "message": "admin message"
        }
        forbidden_states = [RequestState.CANCELED, RequestState.ACCEPTED, RequestState.PROCESSING, RequestState.FAILED,
                            RequestState.COMPLETE, RequestState.REJECTED, RequestState.ARCHIVED, RequestState.NEED_INFO]
        for forbidden_state in forbidden_states:
            self.test_request.state = forbidden_state
            self.test_request.save()
            response = self.client.post(url, data=data)
            self.assertEqual(403, response.status_code)

    def test_request_re_submit(self):
        self.test_request.state = RequestState.NEED_INFO
        self.test_request.save()
        args = {
            'pk': self.test_request.id
        }
        data = {'content': 're-submited'}
        url = reverse('service_catalog:request_re_submit', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.test_request.refresh_from_db()
        self.assertEqual(self.test_request.state, RequestState.SUBMITTED)

    def test_admin_cannot_request_re_submit_on_forbidden_states(self):
        args = {
            'pk': self.test_request.id
        }
        data = {'content': 're-submited'}
        url = reverse('service_catalog:request_re_submit', kwargs=args)
        forbidden_states = [RequestState.CANCELED, RequestState.ACCEPTED, RequestState.PROCESSING, RequestState.FAILED,
                            RequestState.COMPLETE, RequestState.ARCHIVED, RequestState.SUBMITTED]
        for forbidden_state in forbidden_states:
            self.test_request.state = forbidden_state
            self.test_request.save()
            response = self.client.post(url, data=data)
            self.assertEqual(403, response.status_code)

    def test_request_reject(self):
        args = {
            'pk': self.test_request.id
        }
        url = reverse('service_catalog:request_reject', kwargs=args)
        data = {
            "content": "admin message"
        }
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.test_request.refresh_from_db()
        self.assertEqual(self.test_request.state, RequestState.REJECTED)
        self.assertEqual(1, RequestMessage.objects.filter(request=self.test_request.id).count())

    def test_admin_cannot_request_reject_on_forbidden_states(self):
        args = {
            'pk': self.test_request.id
        }
        url = reverse('service_catalog:request_reject', kwargs=args)
        data = {
            "message": "admin message"
        }
        forbidden_states = [RequestState.CANCELED, RequestState.PROCESSING, RequestState.FAILED, RequestState.COMPLETE,
                            RequestState.REJECTED, RequestState.ARCHIVED]
        for forbidden_state in forbidden_states:
            print(forbidden_state)
            self.test_request.state = forbidden_state
            self.test_request.save()
            response = self.client.post(url, data=data)
            self.assertEqual(403, response.status_code)

    def _accept_request_with_expected_state(self, expected_request_state, expected_instance_state, custom_data=None,
                                            status=302):
        args = {
            'pk': self.test_request.id
        }
        if custom_data:
            data = custom_data
        else:
            data = {
                'text_variable': 'my_var',
                'multiplechoice_variable': 'choice1',
                'multiselect_var': 'multiselect_1',
                'textarea_var': '2',
                'password_var': 'password1234',
                'integer_var': '1',
                'float_var': '0.6'
            }

        url = reverse('service_catalog:request_accept', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url, data=data)
        self.assertEqual(status, response.status_code)
        self.test_request.refresh_from_db()
        self.assertEqual(self.test_request.state, expected_request_state)
        self.test_instance.refresh_from_db()
        self.assertEqual(self.test_instance.state, expected_instance_state)
        if response.status_code == 302:
            self.assertEqual(self.test_request.accepted_by, self.superuser)

    def test_request_accept_pending_instance(self):
        self._accept_request_with_expected_state(expected_request_state=RequestState.ACCEPTED,
                                                 expected_instance_state=InstanceState.PENDING)

    def test_request_accept_and_request_pending_instance(self):
        data = {
            'quota_scope_id': self.test_quota_scope.id,
            'text_variable': 'my_var',
            'multiplechoice_variable': 'choice1',
            'multiselect_var': 'multiselect_1',
            'textarea_var': '2',
            'password_var': 'password1234',
            'integer_var': '1',
            'float_var': '0.6',
            'accept_and_process': 'accept_and_process'
        }
        with mock.patch("service_catalog.models.request.Request.perform_processing") as mock_towerlib_call:
            self._accept_request_with_expected_state(expected_request_state=RequestState.PROCESSING,
                                                     expected_instance_state=InstanceState.PROVISIONING,
                                                     custom_data=data)
            mock_towerlib_call.assert_called()

    def test_request_accept_pending_instance_missing_not_required_field(self):
        data = {
            'quota_scope_id': self.test_quota_scope.id,
            'text_variable': 'my_var',
            'multiplechoice_variable': 'choice1',
            'multiselect_var': 'multiselect_1',
            'textarea_var': '2',
            'password_var': 'password1234',
            'float_var': '0.6'
        }
        self._accept_request_with_expected_state(expected_request_state=RequestState.ACCEPTED,
                                                 expected_instance_state=InstanceState.PENDING,
                                                 custom_data=data)

    def test_admin_request_cannot_accept_pending_instance_missing_required_field(self):
        data = {
            'name': self.test_request.instance.name,
            'quota_scope_id': self.test_quota_scope.id,
            'text_variable': 'my_var',
            'multiplechoice_variable': 'choice1',
            'multiselect_var': 'multiselect_1',
            'textarea_var': '2',
            'password_var': 'password1234'
        }
        self._accept_request_with_expected_state(expected_request_state=self.test_request.state,
                                                 expected_instance_state=self.test_instance.state,
                                                 custom_data=data,
                                                 status=200)

    def test_request_accept_accepted_instance(self):
        self._accept_request_with_expected_state(expected_request_state=RequestState.ACCEPTED,
                                                 expected_instance_state=InstanceState.PENDING)
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
        self.assertDictEqual(self.test_request.full_survey, data_expected)
        self.assertEqual(self.test_request.fill_in_survey, old_survey)
        self.assertEqual(self.test_request.admin_fill_in_survey, data_expected)

    def test_request_accept_failed_update(self):
        self.test_instance.state = InstanceState.UPDATE_FAILED
        self.test_instance.save()
        self.test_request.state = RequestState.FAILED
        self.test_request.save()
        self._accept_request_with_expected_state(expected_request_state=RequestState.ACCEPTED,
                                                 expected_instance_state=InstanceState.AVAILABLE)

    def test_request_accept_failed_provisioning(self):
        self.test_instance.state = InstanceState.PROVISION_FAILED
        self.test_instance.save()
        self.test_request.state = RequestState.FAILED
        self.test_request.save()
        self._accept_request_with_expected_state(expected_request_state=RequestState.ACCEPTED,
                                                 expected_instance_state=InstanceState.PENDING)

    def test_request_accept_failed_delete(self):
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
            'pk': self.test_request.id
        }
        url = reverse('service_catalog:request_process', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        with mock.patch("service_catalog.models.job_templates.JobTemplate.execute") as mock_job_execute:
            if isinstance(mock_value, Exception):
                mock_job_execute.side_effect = mock_value
            else:
                mock_job_execute.return_value = mock_value
            response = self.client.post(url)
            self.assertEqual(302, response.status_code)
            self.test_request.refresh_from_db()
            self.assertEqual(self.test_request.processed_by, self.superuser)
            self.assertEqual(self.test_request.state, expected_request_state)
            expected_extra_vars = {
                'text_variable': 'my_var',
                'multiplechoice_variable': "choice1",
                'multiselect_var': ["multiselect_3", "multiselect_2"],
                'textarea_var': "textarea_val",
                'password_var': "password_val",
                'float_var': 1.5,
                'integer_var': 1
            }
            expected_request = {
                'id': self.test_request.id,
                'state': RequestState.PROCESSING,
                'operation': self.test_request.operation.id,
            }
            expected_instance = {
                'id': self.test_instance.id,
                'name': 'test_instance_1',
                'spec': {},
                'state': str(expected_instance_state),
                'service': self.test_request.operation.service.id,
                'quota_scope': ScopeSerializer(self.test_request.instance.quota_scope).data,
                'requester': UserSerializer(self.test_request.instance.requester).data
            }
            self.test_instance.refresh_from_db()
            self.assertEqual(self.test_instance.state, expected_instance_state)
            if not isinstance(mock_value, Exception):
                self.assertIsNotNone(self.test_request.periodic_task)
                mock_job_execute.assert_called()
                kwargs = mock_job_execute.call_args[1]
                expected_data_list = [expected_extra_vars, expected_request, expected_instance]
                try:
                    test_resource = kwargs.get("extra_vars", None).get('squest', None).get('request', None).get('instance', None).get(
                        'resources', None)[0]  # we know that we've only one resource
                    expected_resources = {
                        'id': self.resource_server.id,
                        'resource_group': self.rg_physical_servers.id,
                        'service_catalog_instance': self.test_instance.id
                    }
                    expected_data_list.append(expected_resources)
                except IndexError:  # resource list is empty
                    test_resource = dict()
                    expected_data_list.append(dict())
                data_list = [
                    kwargs.get("extra_vars", None),
                    kwargs.get("extra_vars", None).get('squest', None).get('request', None),
                    kwargs.get("extra_vars", None).get('squest', None).get('request', None).get('instance', None),
                    test_resource
                ]
                for expected_data, data in zip(expected_data_list, data_list):
                    for key_var, val_var in expected_data.items():
                        self.assertIn(key_var, data.keys())
                        self.assertEqual(val_var, data[key_var])

    def test_request_process_new_instance(self):
        self.test_request.state = RequestState.ACCEPTED
        self.test_request.save()
        self._process_with_expected_instance_state(InstanceState.PROVISIONING)

    def test_request_process_new_instance_full_survey_enabled(self):
        enabled_survey_fields = {
            'text_variable': True,
            'multiplechoice_variable': True,
            'multiselect_var': True,
            'textarea_var': True,
            'password_var': True,
            'float_var': True,
            'integer_var': True
        }
        self.test_request.operation.switch_survey_fields_enable_from_dict(enabled_survey_fields)
        full_survey = {
            'text_variable': 'my_var',
            'multiplechoice_variable': "choice1",
            'multiselect_var': ["multiselect_3", "multiselect_2"],
            'textarea_var': "textarea_val",
            'password_var': "password_val",
            'float_var': 1.5,
            'integer_var': 1
        }
        self.test_request.operation.save()
        self.test_request.refresh_from_db()
        self.assertEqual(self.test_request.admin_fill_in_survey, {})
        self.assertEqual(self.test_request.fill_in_survey, full_survey)
        self.assertEqual(self.test_request.full_survey, full_survey)
        self.test_request.state = RequestState.ACCEPTED
        self.test_request.save()
        self._process_with_expected_instance_state(InstanceState.PROVISIONING)

    def test_request_process_new_instance_full_survey_disabled(self):
        enabled_survey_fields = {
            'text_variable': False,
            'multiplechoice_variable': False,
            'multiselect_var': False,
            'textarea_var': False,
            'password_var': False,
            'float_var': False,
            'integer_var': False
        }
        self.test_request.operation.switch_survey_fields_enable_from_dict(enabled_survey_fields)
        full_survey = {
            'text_variable': 'my_var',
            'multiplechoice_variable': "choice1",
            'multiselect_var': ["multiselect_3", "multiselect_2"],
            'textarea_var': "textarea_val",
            'password_var': "password_val",
            'float_var': 1.5,
            'integer_var': 1
        }
        self.test_request.operation.save()
        self.test_request.refresh_from_db()
        self.assertEqual(self.test_request.fill_in_survey, {})
        self.assertEqual(self.test_request.admin_fill_in_survey, full_survey)
        self.assertEqual(self.test_request.full_survey, full_survey)
        self.test_request.state = RequestState.ACCEPTED
        self.test_request.save()
        self._process_with_expected_instance_state(InstanceState.PROVISIONING)

    def test_request_process_update_instance(self):
        self.test_instance.state = InstanceState.AVAILABLE
        self.test_instance.save()
        self.test_request.state = RequestState.ACCEPTED
        self.test_request.operation = self.update_operation_test
        self.test_request.save()
        self._process_with_expected_instance_state(InstanceState.UPDATING)

    def test_request_process_update_instance_with_attached_resource(self):
        self.resource_server.service_catalog_instance = self.test_instance
        self.resource_server.save()
        self.test_instance.state = InstanceState.AVAILABLE
        self.test_instance.save()
        self.test_request.state = RequestState.ACCEPTED
        self.test_request.operation = self.update_operation_test
        self.test_request.save()
        self._process_with_expected_instance_state(InstanceState.UPDATING)

    def test_request_process_delete_instance(self):
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
            'pk': request_update.id
        }
        url = reverse('service_catalog:request_process', kwargs=args)
        response = self.client.post(url)
        self.assertEqual(403, response.status_code)

    def test_request_process_new_instance_on_non_exist_job_template_id(self):
        self.test_request.state = RequestState.ACCEPTED
        self.test_request.save()
        self._process_with_expected_instance_state(InstanceState.PROVISION_FAILED, RequestState.FAILED,
                                                   ExceptionServiceCatalog.JobTemplateNotFound(
                                                       ansible_controller_name=self.ansible_controller_test.name,
                                                       job_template_id=self.job_template_test.ansible_controller_id))
        self.test_request.refresh_from_db()
        self.assertIsNotNone(self.test_request.failure_message)

    def _validate_access_request_details(self):
        args = {
            'pk': self.test_request.id
        }
        url = reverse('service_catalog:request_details', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def _refused_access_request_details(self, status_code=302):
        args = {
            'pk': self.test_request.id
        }
        url = reverse('service_catalog:request_details', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(status_code, response.status_code)

    def test_admin_request_details(self):
        self._validate_access_request_details()


    def test_not_logged_cannot_access_request_details(self):
        self.client.logout()
        self._refused_access_request_details()

    def test_admin_can_delete_request(self):
        args = {
            'pk': self.test_request.id
        }
        url = reverse('service_catalog:request_delete', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.client.post(url)
        self.assertFalse(Request.objects.filter(id=self.test_request.id).exists())

    def test_customer_cannot_delete_request(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        args = {
            'pk': self.test_request.id
        }
        url = reverse('service_catalog:request_delete', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        self.client.post(url)
        self.assertTrue(Request.objects.filter(id=self.test_request.id).exists())

    def test_request_archive_toggle(self):
        self.test_request.state = RequestState.COMPLETE
        self.test_request.save()
        args = {
            'pk': self.test_request.id
        }
        url = reverse('service_catalog:request_archive', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.test_request.refresh_from_db()
        self.assertEqual(self.test_request.state, RequestState.ARCHIVED)
        url = reverse('service_catalog:request_unarchive', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.test_request.refresh_from_db()
        self.assertEqual(self.test_request.state, RequestState.COMPLETE)

    def test_admin_cannot_request_archive_on_forbidden_states(self):
        args = {
            'pk': self.test_request.id
        }
        url = reverse('service_catalog:request_archive', kwargs=args)
        forbidden_states = [RequestState.CANCELED, RequestState.ACCEPTED, RequestState.PROCESSING, RequestState.FAILED,
                            RequestState.REJECTED, RequestState.SUBMITTED, RequestState.NEED_INFO,
                            RequestState.ARCHIVED]
        for forbidden_state in forbidden_states:
            self.test_request.state = forbidden_state
            self.test_request.save()
            response = self.client.get(url)
            self.assertEqual(403, response.status_code)

    def test_admin_cannot_request_unarchive_on_forbidden_states(self):
        args = {
            'pk': self.test_request.id
        }
        url = reverse('service_catalog:request_unarchive', kwargs=args)
        forbidden_states = [RequestState.CANCELED, RequestState.ACCEPTED, RequestState.PROCESSING, RequestState.FAILED,
                            RequestState.REJECTED, RequestState.SUBMITTED, RequestState.NEED_INFO,
                            RequestState.COMPLETE]
        for forbidden_state in forbidden_states:
            self.test_request.state = forbidden_state
            self.test_request.save()
            response = self.client.get(url)
            self.assertEqual(403, response.status_code)

    def test_customer_can_list_his_archived_requests(self):
        self.test_request = Request.objects.create(fill_in_survey={},
                                                   instance=self.test_instance,
                                                   operation=self.create_operation_test,
                                                   user=self.standard_user,
                                                   state=RequestState.ARCHIVED)
        # fist user has one request
        url = reverse('service_catalog:request_archived_list')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data), 1)
        self.client.logout()
        # second user has no request
        self.client.login(username=self.standard_user_2, password=self.common_password)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data), 0)

    def test_cannot_get_archived_requests_list_when_logout(self):
        self.client.logout()
        url = reverse('service_catalog:request_archived_list')
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)

    def test_admin_can_edit_request(self):
        self._edit_request()

    def test_customer_cannot_edit_request(self):
        self.client.force_login(self.standard_user)
        self._edit_request(403)

    def test_cannot_edit_request_when_logout(self):
        self.client.logout()
        self._edit_request(302)

    def _edit_request(self, status_code=200):
        args = {
            'pk': self.test_request.id
        }
        data = {
            "fill_in_survey": "{}",
            "instance": self.test_instance.id,
            "operation": self.create_operation_test.id,
            "user": self.standard_user.id,
            "date_complete": "",
            "date_archived": "",
            "remote_job_id": "",
            "state": "FAILED",
            "periodic_task": "",
            "periodic_task_date_expire": "",
            "failure_message": ""
        }
        url = reverse('service_catalog:request_edit', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(status_code, response.status_code)
        if status_code == 200:
            response = self.client.post(url, data=data)
            self.assertEqual(response.status_code, 302)
