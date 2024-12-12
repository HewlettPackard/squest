from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView, \
    TestingPatchContextView, TestingPutContextView, TestingDeleteContextView
from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2API


class TestResourceTrackerV2ResourceGroupPermissionsEndpoint(BaseTestResourceTrackerV2API, TestPermissionEndpoint):
    def test_resourcegroup_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_resourcegroup_list_create',
                perm_str_list=['resource_tracker_v2.list_resourcegroup'],
            ),
            TestingPostContextView(
                url='api_resourcegroup_list_create',
                perm_str_list=['resource_tracker_v2.add_resourcegroup'],
                data={
                    'name': 'New Resource Group',
                    'tags': ["testTag"]
                }
            ),
            TestingGetContextView(
                url='api_resourcegroup_details',
                perm_str_list=['resource_tracker_v2.view_resourcegroup'],
                url_kwargs={'pk': self.cluster.id}
            ),
            TestingPutContextView(
                url='api_resourcegroup_details',
                perm_str_list=['resource_tracker_v2.change_resourcegroup'],
                data={
                    'name': 'Resource Group PUT',
                    'tags': ["testTag"]
                },
                url_kwargs={'pk': self.cluster.id}
            ),
            TestingPatchContextView(
                url='api_resourcegroup_details',
                perm_str_list=['resource_tracker_v2.change_resourcegroup'],
                data={
                    'name': 'Resource Group PATCH',
                },
                url_kwargs={'pk': self.cluster.id}
            ),
            TestingDeleteContextView(
                url='api_resourcegroup_details',
                perm_str_list=['resource_tracker_v2.delete_resourcegroup'],
                url_kwargs={'pk': self.cluster.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)