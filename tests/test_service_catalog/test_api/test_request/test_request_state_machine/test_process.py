from unittest import mock

from django.urls import reverse

from service_catalog.models import RequestState, InstanceState
from tests.test_service_catalog.base_test_request import BaseTestRequest


AUTHORIZED_STATES = [RequestState.ACCEPTED, RequestState.FAILED]


class TestApiRequestProcess(BaseTestRequest):

    def setUp(self):
        super(TestApiRequestProcess, self).setUp()
        self.test_instance.state = InstanceState.PENDING
        self.test_instance.save()

    def _process(self, status=200, expected_instance_state=InstanceState.PROVISIONING,
                 expected_request_state=RequestState.PROCESSING):
        with mock.patch("service_catalog.models.job_templates.JobTemplate.execute") as mock_job_execute:
            mock_job_execute.return_value = 10
            response = self.client.post(reverse('api_request_process', kwargs={'pk': self.test_request.id}))
            self.assertEqual(status, response.status_code)
            self.test_request.refresh_from_db()
            self.assertEqual(self.test_request.state, expected_request_state)
            expected_extra_vars = {
                'text_variable': 'my_var',
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
                'billing_group': None,
                'spoc': self.test_request.instance.spoc.id
            }
            self.test_instance.refresh_from_db()
            self.assertEqual(self.test_instance.state, expected_instance_state)
            if status == 200:
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

    def test_admin_can_process_request_accepted(self):
        self.test_request.state = RequestState.ACCEPTED
        self.test_request.save()
        self._process()

    def test_admin_can_process_request_failed(self):
        self.test_request.state = RequestState.FAILED
        self.test_request.save()
        self._process()

    def test_admin_cannot_process_request_in_forbidden_state(self):
        forbidden_state = RequestState.values
        for state in AUTHORIZED_STATES:
            forbidden_state.remove(state)
        for state in forbidden_state:
            self.test_request.state = state
            self.test_request.save()
            self._process(status=403, expected_request_state=state, expected_instance_state=InstanceState.PENDING)

    def test_user_cannot_process_request(self):
        self.client.logout()
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._process(status=403, expected_request_state=state,
                          expected_instance_state=InstanceState.PENDING)

    def test_cannot_process_request_when_logout(self):
        self.client.logout()
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._process(status=403, expected_request_state=state,
                          expected_instance_state=InstanceState.PENDING)
