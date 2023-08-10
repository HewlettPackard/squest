from service_catalog.models import RequestState
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogRequestPermissionsProcessView(BaseTestRequest, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.test_request.state = RequestState.ACCEPTED
        self.test_request.save()

    def test_process_view(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:request_process',
                perm_str='service_catalog.process_request',
                url_kwargs={'pk': self.test_request.id},
            ),
            TestingPostContextView(
                url='service_catalog:request_process',
                perm_str='service_catalog.process_request',
                url_kwargs={'pk': self.test_request.id},
            )
        ]
        self.run_permissions_tests(testing_view_list)
