from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogJobTemplatePermissionsViews(BaseTestRequest, TestPermissionEndpoint):
    def test_jobtemplate_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:jobtemplate_list',
                perm_str='service_catalog.list_jobtemplate',
                url_kwargs={'tower_id': self.tower_server_test.id},
            ),
            TestingGetContextView(
                url='service_catalog:jobtemplate_details',
                perm_str='service_catalog.view_jobtemplate',
                url_kwargs={'tower_id': self.tower_server_test.id, 'pk': self.job_template_test.id}
            ),
            TestingGetContextView(
                url='service_catalog:job_template_compliancy',
                perm_str='service_catalog.view_jobtemplate',
                url_kwargs={'tower_id': self.tower_server_test.id, 'pk': self.job_template_test.id}
            ),
            TestingGetContextView(
                url='service_catalog:jobtemplate_delete',
                perm_str='service_catalog.delete_jobtemplate',
                url_kwargs={'tower_id': self.tower_server_test.id, 'pk': self.job_template_test.id}
            ),
            TestingPostContextView(
                url='service_catalog:jobtemplate_delete',
                perm_str='service_catalog.delete_jobtemplate',
                url_kwargs={'tower_id': self.tower_server_test.id, 'pk': self.job_template_test.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)
