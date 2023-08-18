from service_catalog.models import RequestState
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogRequestAcceptPermissionsEndpoint(BaseTestRequestAPI, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.test_request.state = RequestState.SUBMITTED
        self.test_request.save()

    def test_accept_view(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_request_accept',
                perm_str='service_catalog.accept_request',
                url_kwargs={'pk': self.test_request.id},
            ),
            TestingPostContextView(
                url='api_request_accept',
                perm_str='service_catalog.accept_request',
                url_kwargs={'pk': self.test_request.id},
                data={
                    'text_variable': "test text var",
                    'multiplechoice_variable': "choice2",
                    'multiselect_var': ["multiselect_3", "multiselect_1"],
                    'textarea_var': "test text area var",
                    'password_var': "test_password",
                    'float_var': 1.2,
                    'integer_var': 6
                },
                expected_status_code=200
            )
        ]
        self.run_permissions_tests(testing_view_list)
