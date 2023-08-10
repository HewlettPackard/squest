from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogRequestPermissionsCRUDViews(BaseTestRequest, TestPermissionEndpoint):
    def test_crud_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:request_list',
                perm_str='service_catalog.list_request',
            ),
            TestingGetContextView(
                url='service_catalog:request_archived_list',
                perm_str='service_catalog.list_request',
            ),
            TestingGetContextView(
                url='service_catalog:request_details',
                perm_str='service_catalog.view_request',
                url_kwargs={'pk': self.test_request.id}
            ),
            TestingGetContextView(
                url='service_catalog:request_edit',
                perm_str='service_catalog.change_request',
                url_kwargs={'pk': self.test_request.id}
            ),
            TestingPostContextView(
                url='service_catalog:request_edit',
                perm_str='service_catalog.change_request',
                url_kwargs={'pk': self.test_request.id},
                data={
                    "fill_in_survey": "{}",
                    "instance": self.test_instance.id,
                    "operation": self.create_operation_test.id,
                    "user": self.standard_user.id,
                    "date_complete": "",
                    "date_archived": "",
                    "tower_job_id": "",
                    "state": "FAILED",
                    "periodic_task": "",
                    "periodic_task_date_expire": "",
                    "failure_message": ""
                }
            ),
            TestingGetContextView(
                url='service_catalog:request_delete',
                perm_str='service_catalog.delete_request',
                url_kwargs={'pk': self.test_request.id}
            ),
            TestingPostContextView(
                url='service_catalog:request_delete',
                perm_str='service_catalog.delete_request',
                url_kwargs={'pk': self.test_request.id},

            )
        ]
        self.run_permissions_tests(testing_view_list)
