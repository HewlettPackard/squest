from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestResourceTrackerV2ResourceGroupPermissionsViews(BaseTestResourceTrackerV2, TestPermissionEndpoint):
    def test_resourcegroup_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='resource_tracker_v2:resourcegroup_list',
                perm_str_list=['resource_tracker_v2.list_resourcegroup'],
            ),
            TestingGetContextView(
                url='resource_tracker_v2:resourcegroup_list_table',
                perm_str_list=['resource_tracker_v2.list_resourcegroup'],
            ),
            TestingGetContextView(
                url='resource_tracker_v2:resource_tracker_graph',
                perm_str_list=['resource_tracker_v2.list_resourcegroup'],
            ),
            TestingGetContextView(
                url='resource_tracker_v2:resourcegroup_create',
                perm_str_list=['resource_tracker_v2.add_resourcegroup'],
            ),
            TestingPostContextView(
                url='resource_tracker_v2:resourcegroup_create',
                perm_str_list=['resource_tracker_v2.add_resourcegroup'],
                data={
                    'name': 'New attribute',
                    'description': 'The description',
                }
            ),
            TestingGetContextView(
                url='resource_tracker_v2:resourcegroup_details',
                perm_str_list=['resource_tracker_v2.view_resourcegroup'],
                url_kwargs={'pk': self.cluster.id}
            ),
            TestingGetContextView(
                url='resource_tracker_v2:resourcegroup_edit',
                perm_str_list=['resource_tracker_v2.change_resourcegroup'],
                url_kwargs={'pk': self.cluster.id}
            ),
            TestingPostContextView(
                url='resource_tracker_v2:resourcegroup_edit',
                perm_str_list=['resource_tracker_v2.change_resourcegroup'],
                url_kwargs={'pk': self.cluster.id},
                data={
                    'name': 'Attribute updated',
                    'description': 'The description updated',
                }
            ),
            TestingGetContextView(
                url='resource_tracker_v2:resourcegroup_delete',
                perm_str_list=['resource_tracker_v2.delete_resourcegroup'],
                url_kwargs={'pk': self.cluster.id}
            ),
            TestingPostContextView(
                url='resource_tracker_v2:resourcegroup_delete',
                perm_str_list=['resource_tracker_v2.delete_resourcegroup'],
                url_kwargs={'pk': self.cluster.id},

            )
        ]
        self.run_permissions_tests(testing_view_list)