from unittest import mock

from django.urls import reverse

from service_catalog.models import Request, Message, RequestMessage
from service_catalog.models.instance import InstanceState
from service_catalog.models.request import RequestState
from tests.base_test_request import BaseTestRequest


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

    def _accept_request_with_expected_state(self, expected_request_state, expected_instance_state):
        args = {
            'request_id': self.test_request.id
        }
        data = {'text_variable': 'my_var',
                'multiplechoice_variable': 'choice1'
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

    def _process_with_expected_instance_state(self, expected_instance_state):
        args = {
            'request_id': self.test_request.id
        }
        url = reverse('service_catalog:admin_request_process', kwargs=args)
        with mock.patch("service_catalog.models.job_templates.JobTemplate.execute") as mock_job_execute:
            mock_job_execute.return_value = 10
            response = self.client.post(url)
            self.assertEquals(302, response.status_code)
            self.test_request.refresh_from_db()
            self.assertEquals(self.test_request.state, RequestState.PROCESSING)
            expected_parameters = {
                'instance_name': 'test instance',
                'text_variable': 'my_var',
                'squest': {
                    'instance': {
                        'id': self.test_instance.id,
                        'name': 'test_instance_1',
                        'spec': {},
                        'state': expected_instance_state,
                        'service': self.test_instance.service.id,
                        'billing_group': None
                    }
                }
            }
            self.test_instance.refresh_from_db()
            self.assertEquals(self.test_instance.state, expected_instance_state)
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
