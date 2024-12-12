from service_catalog.models import RequestState, Request
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogRequestPermissionsCRUDView(BaseTestRequest, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.test_request.state = RequestState.ARCHIVED
        self.test_request.save()

    def test_bulk_delete_view(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:request_bulk_delete',
                perm_str_list=['service_catalog.delete_request'],
                data={
                    'selection': [request.id for request in Request.objects.all()]

                }
            ),
            TestingPostContextView(
                url='service_catalog:request_bulk_delete',
                perm_str_list=['service_catalog.delete_request'],
                data={
                    'selection': [request.id for request in Request.objects.all()]

                }
            )
        ]
        self.run_permissions_tests(testing_view_list)