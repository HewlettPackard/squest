from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestResourceTrackerV2ResourcePermissionsViews(BaseTestResourceTrackerV2, TestPermissionEndpoint):
    def test_resource_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='resource_tracker_v2:resource_list',
                perm_str_list=['resource_tracker_v2.list_resource'],
                url_kwargs={'resource_group_id': self.single_vms.id}
            ),
            TestingGetContextView(
                url='resource_tracker_v2:resource_create',
                perm_str_list=['resource_tracker_v2.add_resource'],
                url_kwargs={'resource_group_id': self.single_vms.id}
            ),
            TestingPostContextView(
                url='resource_tracker_v2:resource_create',
                perm_str_list=['resource_tracker_v2.add_resource'],
                url_kwargs={'resource_group_id': self.single_vms.id},
                data={
                    'name': 'vm3',
                    'service_catalog_instance': '',
                    'is_deleted_on_instance_deletion': True,
                    'resource_group': self.single_vms.id
                }
            ),
            TestingGetContextView(
                url='resource_tracker_v2:resource_edit',
                perm_str_list=['resource_tracker_v2.change_resource'],
                url_kwargs={'resource_group_id': self.single_vms.id, 'pk': self.vm1.id}
            ),
            TestingPostContextView(
                url='resource_tracker_v2:resource_edit',
                perm_str_list=['resource_tracker_v2.change_resource'],
                url_kwargs={'resource_group_id': self.single_vms.id, 'pk': self.vm1.id},
                data={
                    'name': 'vm updated',
                    'service_catalog_instance': '',
                    'is_deleted_on_instance_deletion': True,
                    'resource_group': self.single_vms.id
                }
            ),
            TestingGetContextView(
                url='resource_tracker_v2:resource_move',
                perm_str_list=['resource_tracker_v2.change_resource'],
                url_kwargs={'resource_group_id': self.single_vms.id, 'pk': self.vm1.id}
            ),
            TestingPostContextView(
                url='resource_tracker_v2:resource_move',
                perm_str_list=['resource_tracker_v2.change_resource'],
                url_kwargs={'resource_group_id': self.single_vms.id, 'pk': self.vm1.id},
                data={
                    'resource_group': self.cluster.id
                }
            ),
            TestingGetContextView(
                url='resource_tracker_v2:resource_delete',
                perm_str_list=['resource_tracker_v2.delete_resource'],
                url_kwargs={'resource_group_id': self.single_vms.id, 'pk': self.vm1.id}
            ),
            TestingPostContextView(
                url='resource_tracker_v2:resource_delete',
                perm_str_list=['resource_tracker_v2.delete_resource'],
                url_kwargs={'resource_group_id': self.single_vms.id, 'pk': self.vm1.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_resource_views_bulk_delete(self):
        testing_view_list = [

            TestingGetContextView(
                url='resource_tracker_v2:resource_bulk_delete',
                perm_str_list=['resource_tracker_v2.delete_resource'],
                url_kwargs={'resource_group_id': self.single_vms.id},
                data={
                    'selection': [resource.id for resource in self.single_vms.resources.all()]

                }),
            TestingPostContextView(
                url='resource_tracker_v2:resource_bulk_delete',
                perm_str_list=['resource_tracker_v2.delete_resource'],
                url_kwargs={'resource_group_id': self.single_vms.id},
                data={
                    'selection': [resource.id for resource in self.single_vms.resources.all()]

                }
            )
        ]
        self.run_permissions_tests(testing_view_list)