from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestResourceTrackerV2TransformerPermissionsViews(BaseTestResourceTrackerV2, TestPermissionEndpoint):
    def test_transformer_views(self):
        self.vcpu_from_core_transformer.delete()
        testing_view_list = [
            TestingGetContextView(
                url='resource_tracker_v2:ajax_load_attribute',
                perm_str='resource_tracker_v2.list_transformer',
                data={
                    'current_resource_group_id': self.single_vms.id,
                    'target_resource_group_id': self.cluster.id
                }
            ),
            TestingGetContextView(
                url='resource_tracker_v2:transformer_list',
                perm_str='resource_tracker_v2.list_transformer',
                url_kwargs={'resource_group_id': self.single_vms.id}
            ),
            TestingGetContextView(
                url='resource_tracker_v2:transformer_create',
                perm_str='resource_tracker_v2.add_transformer',
                url_kwargs={'resource_group_id': self.single_vms.id}
            ),
            TestingPostContextView(
                url='resource_tracker_v2:transformer_create',
                perm_str='resource_tracker_v2.add_transformer',
                url_kwargs={'resource_group_id': self.single_vms.id},
                data={
                    'attribute_definition': self.vcpu_attribute.id,
                    'consume_from_resource_group': self.cluster.id,
                    'consume_from_attribute_definition': self.core_attribute.id,
                    'factor': 1,
                }
            ),
            TestingGetContextView(
                url='resource_tracker_v2:transformer_edit',
                perm_str='resource_tracker_v2.change_transformer',
                url_kwargs={'resource_group_id': self.single_vms.id, 'attribute_id': self.vcpu_attribute.id}
            ),
            TestingPostContextView(
                url='resource_tracker_v2:transformer_edit',
                perm_str='resource_tracker_v2.change_transformer',
                url_kwargs={'resource_group_id': self.single_vms.id, 'attribute_id': self.vcpu_attribute.id},
                data={
                    'attribute_definition': self.vcpu_attribute.id,
                    'consume_from_resource_group': self.cluster.id,
                    'consume_from_attribute_definition': self.core_attribute.id,
                    'factor': 2,
                }
            ),
            TestingGetContextView(
                url='resource_tracker_v2:transformer_delete',
                perm_str='resource_tracker_v2.delete_transformer',
                url_kwargs={'resource_group_id': self.single_vms.id, 'attribute_id': self.vcpu_attribute.id}
            ),
            TestingPostContextView(
                url='resource_tracker_v2:transformer_delete',
                perm_str='resource_tracker_v2.delete_transformer',
                url_kwargs={'resource_group_id': self.single_vms.id, 'attribute_id': self.vcpu_attribute.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)
