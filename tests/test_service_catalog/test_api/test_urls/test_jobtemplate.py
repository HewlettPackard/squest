from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView, \
    TestingPatchContextView, TestingPutContextView, TestingDeleteContextView
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestServiceCatalogJobTemplatePermissionsEndpoint(BaseTestRequestAPI, TestPermissionEndpoint):

    def test_jobtemplate_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_jobtemplate_list',
                perm_str='service_catalog.list_jobtemplate',
                url_kwargs={'tower_server_id': self.job_template_test.tower_server.id}
            ),
            TestingPostContextView(
                url='api_jobtemplate_list',
                perm_str='service_catalog.add_jobtemplate',
                url_kwargs={'tower_server_id': self.job_template_test.tower_server.id},
                expected_status_code=405,
                expected_not_allowed_status_code=405
            ),
            TestingGetContextView(
                url='api_jobtemplate_details',
                perm_str='service_catalog.view_jobtemplate',
                url_kwargs={'tower_server_id': self.job_template_test.tower_server.id, 'pk': self.job_template_test.id},
            ),
            TestingPutContextView(
                url='api_jobtemplate_details',
                perm_str='service_catalog.change_jobtemplate',
                url_kwargs={'tower_server_id': self.job_template_test.tower_server.id, 'pk': self.job_template_test.id},
                expected_status_code=405,
                expected_not_allowed_status_code=405
            ),
            TestingPatchContextView(
                url='api_jobtemplate_details',
                perm_str='service_catalog.change_jobtemplate',
                url_kwargs={'tower_server_id': self.job_template_test.tower_server.id, 'pk': self.job_template_test.id},
                expected_status_code=405,
                expected_not_allowed_status_code=405
            ),
            TestingDeleteContextView(
                url='api_jobtemplate_details',
                perm_str='service_catalog.delete_jobtemplate',
                url_kwargs={'tower_server_id': self.job_template_test.tower_server.id, 'pk': self.job_template_test.id},
                expected_status_code=405,
                expected_not_allowed_status_code=405
            )
        ]
        self.run_permissions_tests(testing_view_list)
