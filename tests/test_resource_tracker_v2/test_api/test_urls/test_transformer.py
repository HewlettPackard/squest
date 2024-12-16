from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView, \
    TestingPatchContextView, TestingPutContextView, TestingDeleteContextView
from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2API


class TestResourceTrackerV2TransformerPermissionsEndpoint(BaseTestResourceTrackerV2API, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.vcpu_from_core_transformer.delete()

    def test_transformer_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_transformer_list_create',
                perm_str_list=['resource_tracker_v2.list_transformer'],
            ),
            TestingPostContextView(
                url='api_transformer_list_create',
                perm_str_list=['resource_tracker_v2.add_transformer'],
                data={
                    'resource_group': self.single_vms.id,
                    'attribute_definition': self.vcpu_attribute.id,
                    'consume_from_resource_group': self.cluster.id,
                    'consume_from_attribute_definition': self.core_attribute.id
                }
            ),
            TestingGetContextView(
                url='api_transformer_details',
                perm_str_list=['resource_tracker_v2.view_transformer'],
                url_kwargs={
                    'pk': self.v_memory_from_memory_transformer.id,
                }
            ),
            TestingPutContextView(
                url='api_transformer_details',
                perm_str_list=['resource_tracker_v2.change_transformer'],
                data={
                    'resource_group': self.single_vms.id,
                    'attribute_definition': self.v_memory_attribute.id,
                    'consume_from_resource_group': self.cluster.id,
                    'consume_from_attribute_definition': self.memory_attribute.id,
                    'factor': 2,
                },
                url_kwargs={
                    'pk': self.v_memory_from_memory_transformer.id,
                }
            ),
            TestingPatchContextView(
                url='api_transformer_details',
                perm_str_list=['resource_tracker_v2.change_transformer'],
                data={
                    'factor': 16,
                },
                url_kwargs={
                    'pk': self.v_memory_from_memory_transformer.id,
                }
            ),
            TestingDeleteContextView(
                url='api_transformer_details',
                perm_str_list=['resource_tracker_v2.delete_transformer'],
                url_kwargs={
                    'pk': self.v_memory_from_memory_transformer.id,
                }
            )
        ]
        self.run_permissions_tests(testing_view_list)