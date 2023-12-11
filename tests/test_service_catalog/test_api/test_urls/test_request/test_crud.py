from service_catalog.models import CustomLink, RequestState
from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView, \
    TestingPatchContextView, TestingPutContextView, TestingDeleteContextView
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestServiceCatalogRequestCRUDPermissionsEndpoint(BaseTestRequestAPI, TestPermissionEndpoint):
    def test_request_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_request_list',
                perm_str='service_catalog.list_request',
            ),
            TestingPostContextView(
                url='api_request_list',
                perm_str='service_catalog.add_request',
                expected_status_code=405,
                expected_not_allowed_status_code=405
            ),
            TestingGetContextView(
                url='api_request_details',
                perm_str='service_catalog.view_request',
                url_kwargs={'pk': self.test_request.id}
            ),
            TestingPutContextView(
                url='api_request_details',
                perm_str='service_catalog.change_request',
                data={
                    'fill_in_survey': dict(),
                    'tower_job_id': 6,
                    'state': RequestState.ON_HOLD,
                    'operation': self.update_operation_test.id,
                    'user': {'id': self.standard_user.id}
                },
                url_kwargs={'pk': self.test_request.id}
            ),
            TestingPatchContextView(
                url='api_request_details',
                perm_str='service_catalog.change_request',
                data={
                    'tower_job_id': 8,
                },
                url_kwargs={'pk': self.test_request.id}
            ),
            TestingDeleteContextView(
                url='api_request_details',
                perm_str='service_catalog.delete_request',
                url_kwargs={'pk': self.test_request.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)
