from service_catalog.models import RequestState
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogRequestPermissionsCancelView(BaseTestRequest, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.test_request.state = RequestState.SUBMITTED
        self.test_request.save()

    def test_cancel_view(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:request_cancel',
                perm_str_list=['service_catalog.cancel_request'],
                url_kwargs={'pk': self.test_request.id},
            ),
            TestingPostContextView(
                url='service_catalog:request_cancel',
                perm_str_list=['service_catalog.cancel_request'],
                url_kwargs={'pk': self.test_request.id},
            )
        ]
        self.run_permissions_tests(testing_view_list)