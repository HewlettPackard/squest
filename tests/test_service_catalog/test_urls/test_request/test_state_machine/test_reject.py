from service_catalog.models import RequestState
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogRequestPermissionsRejectView(BaseTestRequest, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.test_request.state = RequestState.SUBMITTED
        self.test_request.save()

    def test_reject_view(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:request_reject',
                perm_str_list=['service_catalog.reject_request'],
                url_kwargs={'pk': self.test_request.id},
            ),
            TestingPostContextView(
                url='service_catalog:request_reject',
                perm_str_list=['service_catalog.reject_request'],
                url_kwargs={'pk': self.test_request.id},
                data={
                    'content': 'My comment'
                }
            )
        ]
        self.run_permissions_tests(testing_view_list)