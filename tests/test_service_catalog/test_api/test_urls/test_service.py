from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView, \
    TestingPatchContextView, TestingPutContextView, TestingDeleteContextView
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestServiceCatalogServicePermissionsEndpoint(BaseTestRequestAPI, TestPermissionEndpoint):
    def test_service_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_service_list_create',
                perm_str='service_catalog.list_service',
            ),
            TestingPostContextView(
                url='api_service_list_create',
                perm_str='service_catalog.add_service',
                data={
                    'name': "New service",
                    'description': "Service description",
                    'enabled': False,
                    'extra_vars': {"test": "test"}
                }
            ),
            TestingPostContextView(
                url='api_service_request_create',
                perm_str='service_catalog.request_on_service',
                url_kwargs={"service_id": self.service_test.id, "pk": self.create_operation_test.id},
                data={
                    'squest_instance_name': 'instance test',
                    'quota_scope': self.test_quota_scope.id,
                    'fill_in_survey': {
                        'text_variable': 'my text'
                    }
                }
            ),
            TestingGetContextView(
                url='api_service_details',
                perm_str='service_catalog.view_service',
                url_kwargs={'pk': self.service_test.id}
            ),
            TestingPutContextView(
                url='api_service_details',
                perm_str='service_catalog.change_service',
                data={
                    'name': "Service PUT",
                    'description': "Service description",
                    'enabled': False,
                    'extra_vars': {"test": "test"}
                },
                url_kwargs={'pk': self.service_test.id}
            ),
            TestingPatchContextView(
                url='api_service_details',
                perm_str='service_catalog.change_service',
                data={
                    'name': 'Service PATCH',
                },
                url_kwargs={'pk': self.service_test.id}
            ),
            TestingDeleteContextView(
                url='api_service_details',
                perm_str='service_catalog.delete_service',
                url_kwargs={'pk': self.service_test.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)
