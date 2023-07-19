from django.urls import reverse

from service_catalog.models import RequestState, Request, Instance
from tests.test_service_catalog.base_test_request import BaseTestRequest

AUTHORIZED_STATES = [RequestState.SUBMITTED, RequestState.ACCEPTED, RequestState.FAILED]


class TestApiRequestAccept(BaseTestRequest):

    def setUp(self):
        super(TestApiRequestAccept, self).setUp()

    def _get_form(self, status=200, request=None, expected=None):
        if request is None:
            request = self.test_request
        response = self.client.get(reverse('api_request_accept', kwargs={'pk': request.id}))
        self.assertEqual(response.status_code, status)
        if status == 200:
            if expected is None:
                expected = {
                    'text_variable': "my_var",
                    'multiplechoice_variable': "choice1",
                    'multiselect_var': ["multiselect_3", "multiselect_2"],
                    'textarea_var': "textarea_val",
                    'password_var': "password_val",
                    'float_var': 1.5,
                    'integer_var': 1
                }
            for key in expected.keys():
                if key != 'multiselect_var':
                    self.assertEqual(response.data[key], expected[key])

    def _accept(self, data=None, request=None, status=200):
        if request is None:
            request = self.test_request
        if data is None:
            data = {
                'text_variable': "test text var",
                'multiplechoice_variable': "choice2",
                'multiselect_var': ["multiselect_3", "multiselect_1"],
                'textarea_var': "test text area var",
                'password_var': "test_password",
                'float_var': 1.2,
                'integer_var': 6
            }
        response = self.client.post(reverse('api_request_accept', kwargs={'pk': request.id}), data=data)
        self.assertEqual(response.status_code, status)
        if status == 200:
            request.refresh_from_db()
            for key in data.keys():
                if isinstance(data[key], list):
                    self.assertEqual(set(data[key]), set(request.full_survey[key]))
                else:
                    self.assertEqual(data[key], request.full_survey[key])
            self.assertEqual(RequestState.ACCEPTED, request.state)

    def test_admin_can_accept_request(self):
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.fill_in_survey = {'text_variable': 'my_var'}
            self.test_request.admin_fill_in_survey = {}
            self.test_request.save()
            self._get_form()
            self._accept()

    def test_admin_can_accept_request_on_empty_survey(self):
        test_instance = Instance.objects.create(name="test_instance_1",
                                                service=self.service_test,
                                                requester=self.standard_user,
                                                quota_scope=self.test_quota_scope)
        test_request = Request.objects.create(fill_in_survey={},
                                              instance=test_instance,
                                              operation=self.create_operation_empty_survey_test,
                                              user=self.standard_user)
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.fill_in_survey = {'text_variable': 'my_var'}
            self.test_request.admin_fill_in_survey = {}
            self.test_request.save()
            self._get_form(request=test_request, expected={})
            self._accept(data={}, request=test_request)

    def test_admin_can_accept_request_with_missing_non_required_field(self):
        data = {
            'text_variable': "test text var",
            'multiplechoice_variable': "choice2",
            'multiselect_var': ["multiselect_3", "multiselect_1"],
            'textarea_var': "test text area var",
            'password_var': "test_password",
            'float_var': 1.2,
        }
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.fill_in_survey = {'text_variable': 'my_var'}
            self.test_request.admin_fill_in_survey = {}
            self.test_request.save()
            self._get_form()
            self._accept(data=data)

    def test_admin_cannot_accept_request_with_missing_field(self):
        data = {
            'text_variable': "test text var",
            'multiplechoice_variable': "choice2",
            'multiselect_var': ["multiselect_3", "multiselect_1"],
            'textarea_var': "test text area var",
            'password_var': "test_password",
            'integer_var': 6,
        }
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._get_form()
            self._accept(data=data, status=400)

    def test_admin_cannot_accept_request_in_forbidden_state(self):
        forbidden_state = RequestState.values
        for state in AUTHORIZED_STATES:
            forbidden_state.remove(state)
        for state in forbidden_state:
            print(state)
            self.test_request.state = state
            self.test_request.save()
            self._get_form(status=403)
            self._accept(status=403)

    def test_user_cannot_accept_request(self):
        self.client.force_login(self.standard_user)
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._get_form(status=403)
            self._accept(status=403)

    def test_cannot_accept_request_when_logout(self):
        self.client.logout()
        for state in AUTHORIZED_STATES:
            self.test_request.state = state
            self.test_request.save()
            self._get_form(status=403)
            self._accept(status=403)
