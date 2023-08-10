from service_catalog.models import RequestState
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogRequestPermissionsAcceptView(BaseTestRequest, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.test_request.state = RequestState.SUBMITTED
        self.test_request.save()

    def test_accept_view(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:request_accept',
                perm_str='service_catalog.accept_request',
                url_kwargs={'pk': self.test_request.id},
            ),
            TestingPostContextView(
                url='service_catalog:request_accept',
                perm_str='service_catalog.accept_request',
                url_kwargs={'pk': self.test_request.id},
                data={
                    'text_variable': 'my_var',
                    'multiplechoice_variable': 'choice1',
                    'multiselect_var': 'multiselect_1',
                    'textarea_var': '2',
                    'password_var': 'password1234',
                    'integer_var': '1',
                    'float_var': '0.6'
                }
            )
        ]
        self.run_permissions_tests(testing_view_list)
