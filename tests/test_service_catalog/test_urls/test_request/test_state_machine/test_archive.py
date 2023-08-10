from service_catalog.models import RequestState
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogRequestPermissionsArchiveView(BaseTestRequest, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.test_request.state = RequestState.COMPLETE
        self.test_request.save()

    def test_archive_view(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:request_archive',
                perm_str='service_catalog.archive_request',
                url_kwargs={'pk': self.test_request.id},
                expected_status_code=302
            ),
            TestingPostContextView(
                url='service_catalog:request_archive',
                perm_str='service_catalog.archive_request',
                url_kwargs={'pk': self.test_request.id},
                expected_not_allowed_status_code=405,
                expected_status_code=405
            )
        ]
        self.run_permissions_tests(testing_view_list)
