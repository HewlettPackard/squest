from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView, \
    TestingPatchContextView, TestingPutContextView, TestingDeleteContextView
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestServiceCatalogTowerServerPermissionsEndpoint(BaseTestRequestAPI, TestPermissionEndpoint):
    def test_towerserver_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_towerserver_list_create',
                perm_str='service_catalog.list_towerserver'
            ),
            TestingPostContextView(
                url='api_towerserver_list_create',
                perm_str='service_catalog.add_towerserver',
                data={
                    'name': "New Tower Server",
                    'host': "my-tower-domain.com",
                    'token': "mytokenverysimple",
                    'secure': True,
                    'ssl_verify': False,
                    'extra_vars': {"test": "test"}
                }
            ),
            TestingPostContextView(
                url='api_jobtemplate_sync_all',
                perm_str='service_catalog.sync_towerserver',
                url_kwargs={'tower_server_id': self.tower_server_test.id},
                expected_status_code=202
            ),
            TestingPostContextView(
                url='api_jobtemplate_sync',
                perm_str='service_catalog.sync_towerserver',
                url_kwargs={'tower_server_id': self.tower_server_test.id, 'job_template_id': self.job_template_test.id},
                expected_status_code=202
            ),
            TestingGetContextView(
                url='api_towerserver_details',
                perm_str='service_catalog.view_towerserver',
                url_kwargs={'pk': self.tower_server_test.id}
            ),
            TestingPutContextView(
                url='api_towerserver_details',
                perm_str='service_catalog.change_towerserver',
                data={
                    'name': 'Tower Server PUT',
                    'host': "my-tower-domain2.com",
                    'token': "mytokenverysimple",
                    'secure': True,
                    'ssl_verify': False,
                    'extra_vars': {"test": "test"}
                },
                url_kwargs={'pk': self.tower_server_test.id}
            ),
            TestingPatchContextView(
                url='api_towerserver_details',
                perm_str='service_catalog.change_towerserver',
                data={
                    'name': 'Tower Server PATCH',
                },
                url_kwargs={'pk': self.tower_server_test.id}
            ),
            TestingDeleteContextView(
                url='api_towerserver_details',
                perm_str='service_catalog.delete_towerserver',
                url_kwargs={'pk': self.tower_server_test.id}
            ),
        ]
        self.run_permissions_tests(testing_view_list)
