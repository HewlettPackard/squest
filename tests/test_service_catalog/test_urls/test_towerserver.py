from unittest import mock

from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogTowerServerPermissionsViews(BaseTestRequest, TestPermissionEndpoint):
    def test_towerserver_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:towerserver_list',
                perm_str_list=['service_catalog.list_towerserver'],
            ),
            TestingGetContextView(
                url='service_catalog:towerserver_create',
                perm_str_list=['service_catalog.add_towerserver'],
            ),
            TestingPostContextView(
                url='service_catalog:towerserver_create',
                perm_str_list=['service_catalog.add_towerserver'],
                data={
                    "name": "New tower",
                    "host": "tower.domain.local",
                    "token": "xxxx",
                    "extra_vars": "{}"
                }
            ),
            TestingGetContextView(
                url='service_catalog:towerserver_details',
                perm_str_list=['service_catalog.view_towerserver'],
                url_kwargs={'pk': self.tower_server_test.id}
            ),
            TestingGetContextView(
                url='service_catalog:towerserver_edit',
                perm_str_list=['service_catalog.change_towerserver'],
                url_kwargs={'pk': self.tower_server_test.id}
            ),
            TestingPostContextView(
                url='service_catalog:towerserver_edit',
                perm_str_list=['service_catalog.change_towerserver'],
                url_kwargs={'pk': self.tower_server_test.id},
                data={
                    "name": "Tower server updated",
                    "host": "https://tower-updated.domain.local",
                    "token": "xxxx-updated"
                }
            ),
            TestingGetContextView(
                url='service_catalog:towerserver_sync',
                perm_str_list=['service_catalog.sync_towerserver'],
                url_kwargs={'tower_id': self.tower_server_test.id},
                expected_status_code=405,
                expected_not_allowed_status_code=405
            ),
            TestingPostContextView(
                url='service_catalog:towerserver_sync',
                perm_str_list=['service_catalog.sync_towerserver'],
                url_kwargs={'tower_id': self.tower_server_test.id},
                expected_status_code=202,
            ),
            TestingGetContextView(
                url='service_catalog:jobtemplate_sync',
                perm_str_list=['service_catalog.sync_towerserver'],
                url_kwargs={'tower_id': self.tower_server_test.id, 'pk': self.job_template_test.id},
                expected_status_code=405,
                expected_not_allowed_status_code=405
            ),
            TestingPostContextView(
                url='service_catalog:jobtemplate_sync',
                perm_str_list=['service_catalog.sync_towerserver'],
                url_kwargs={'tower_id': self.tower_server_test.id, 'pk': self.job_template_test.id},
                expected_status_code=202,
            ),
            TestingGetContextView(
                url='service_catalog:towerserver_delete',
                perm_str_list=['service_catalog.delete_towerserver'],
                url_kwargs={'pk': self.tower_server_test.id}
            ),
            TestingPostContextView(
                url='service_catalog:towerserver_delete',
                perm_str_list=['service_catalog.delete_towerserver'],
                url_kwargs={'pk': self.tower_server_test.id}
            )
        ]
        with mock.patch("towerlib.towerlib.Tower.__init__") as mock_tower_lib:
            with mock.patch("service_catalog.models.tower_server.TowerServer.sync") as mock_tower_sync:
                mock_tower_lib.return_value = None
                self.run_permissions_tests(testing_view_list)