from service_catalog.models import Instance
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogInstancePermissionsBulkDeleteView(BaseTestRequest, TestPermissionEndpoint):
    def test_bulk_delete_view(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:instance_bulk_delete',
                perm_str_list=['service_catalog.delete_instance'],
                data={
                    'selection': [instance.id for instance in Instance.objects.all()]

                }),
            TestingPostContextView(
                url='service_catalog:instance_bulk_delete',
                perm_str_list=['service_catalog.delete_instance'],
                data={
                    'selection': [instance.id for instance in Instance.objects.all()]

                }
            )
        ]
        self.run_permissions_tests(testing_view_list)