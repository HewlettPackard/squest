
from service_catalog.models import Doc
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestPermissionEndpoint


class TestServiceCatalogDocPermissionsViews(BaseTestRequest, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.doc = Doc.objects.create(title="test_doc", content="# tittle 1")

    def test_doc_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:doc_list',
                perm_str_list=['service_catalog.list_doc'],
            ),
            TestingGetContextView(
                url='service_catalog:doc_details',
                perm_str_list=['service_catalog.view_doc'],
                url_kwargs={'pk': self.doc.id}
            ),

        ]
        self.run_permissions_tests(testing_view_list)