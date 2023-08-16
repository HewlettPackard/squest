from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView, \
    TestingPatchContextView, TestingPutContextView, TestingDeleteContextView
from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2API


class TestResourceTrackerV2ResourcePermissionsEndpoint(BaseTestResourceTrackerV2API, TestPermissionEndpoint):
    def test_resource_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_resource_list_create',
                perm_str='resource_tracker_v2.list_resource',
                url_kwargs={'resource_group_id': self.single_vms.id},
            ),
            TestingPostContextView(
                url='api_resource_list_create',
                perm_str='resource_tracker_v2.add_resource',
                url_kwargs={'resource_group_id': self.single_vms.id},
                data={
                    'name': 'New Resource',
                    'resource_attributes': [
                        {
                            'name': self.vcpu_attribute.name,
                            'value': 2,
                        },
                        {
                            'name': self.v_memory_attribute.name,
                            'value': 4,
                        },
                    ],
                }
            ),
            TestingGetContextView(
                url='api_resource_details',
                perm_str='resource_tracker_v2.view_resource',
                url_kwargs={'resource_group_id': self.single_vms.id, 'pk': self.vm1.id}
            ),
            TestingPutContextView(
                url='api_resource_details',
                perm_str='resource_tracker_v2.change_resource',
                data={
                    'name': 'Resource PUT',
                    'resource_attributes': [
                        {
                            'name': self.vcpu_attribute.name,
                            'value': 4,
                        },
                        {
                            'name': self.v_memory_attribute.name,
                            'value': 16,
                        },
                    ]
                },
                url_kwargs={'resource_group_id': self.single_vms.id, 'pk': self.vm1.id}
            ),
            TestingPatchContextView(
                url='api_resource_details',
                perm_str='resource_tracker_v2.change_resource',
                data={
                    'name': 'Resource PATCH',
                },
                url_kwargs={'resource_group_id': self.single_vms.id, 'pk': self.vm1.id}
            ),
            TestingDeleteContextView(
                url='api_resource_details',
                perm_str='resource_tracker_v2.delete_resource',
                url_kwargs={'resource_group_id': self.single_vms.id, 'pk': self.vm1.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)
