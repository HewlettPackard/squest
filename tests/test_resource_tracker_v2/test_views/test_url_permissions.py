from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2
from tests.views import TestingGetUIViews, TestingPostUIViews, TestPermissionUIViews


class TestResourceTrackerV2PermissionsViews(BaseTestResourceTrackerV2, TestPermissionUIViews):

    def test_attributedefinition_views(self):
        testing_view_list = [
            TestingGetUIViews(
                url='resource_tracker_v2:attributedefinition_list',
                perm_str='resource_tracker_v2.list_attributedefinition',
            ),
            TestingGetUIViews(
                url='resource_tracker_v2:attributedefinition_details',
                perm_str='resource_tracker_v2.view_attributedefinition',
                url_kwargs={'pk': self.core_attribute.id}
            ),
            TestingGetUIViews(
                url='resource_tracker_v2:attributedefinition_create',
                perm_str='resource_tracker_v2.add_attributedefinition',
            ),
            TestingPostUIViews(
                url='resource_tracker_v2:attributedefinition_create',
                perm_str='resource_tracker_v2.add_attributedefinition',
                data={
                    'name': 'New attribute',
                    'description': 'The description',
                }
            ),
            TestingGetUIViews(
                url='resource_tracker_v2:attributedefinition_edit',
                perm_str='resource_tracker_v2.change_attributedefinition',
                url_kwargs={'pk': self.core_attribute.id}
            ),
            TestingPostUIViews(
                url='resource_tracker_v2:attributedefinition_edit',
                perm_str='resource_tracker_v2.change_attributedefinition',
                url_kwargs={'pk': self.core_attribute.id},
                data={
                    'name': 'Attribute updated',
                    'description': 'The description updated',
                }
            ),
            TestingGetUIViews(
                url='resource_tracker_v2:attributedefinition_delete',
                perm_str='resource_tracker_v2.delete_attributedefinition',
                url_kwargs={'pk': self.core_attribute.id}
            ),
            TestingPostUIViews(
                url='resource_tracker_v2:attributedefinition_delete',
                perm_str='resource_tracker_v2.delete_attributedefinition',
                url_kwargs={'pk': self.core_attribute.id},

            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_resourcegroup_views(self):
        testing_view_list = [
            TestingGetUIViews(
                url='resource_tracker_v2:resourcegroup_list',
                perm_str='resource_tracker_v2.list_resourcegroup',
            ),
            TestingGetUIViews(
                url='resource_tracker_v2:resourcegroup_list_table',
                perm_str='resource_tracker_v2.list_resourcegroup',
            ),
            TestingGetUIViews(
                url='resource_tracker_v2:resource_tracker_graph',
                perm_str='resource_tracker_v2.list_resourcegroup',
            ),
            TestingGetUIViews(
                url='resource_tracker_v2:resourcegroup_create',
                perm_str='resource_tracker_v2.add_resourcegroup',
            ),
            TestingPostUIViews(
                url='resource_tracker_v2:resourcegroup_create',
                perm_str='resource_tracker_v2.add_resourcegroup',
                data={
                    'name': 'New attribute',
                    'description': 'The description',
                }
            ),
            TestingGetUIViews(
                url='resource_tracker_v2:resourcegroup_edit',
                perm_str='resource_tracker_v2.change_resourcegroup',
                url_kwargs={'pk': self.cluster.id}
            ),
            TestingPostUIViews(
                url='resource_tracker_v2:resourcegroup_edit',
                perm_str='resource_tracker_v2.change_resourcegroup',
                url_kwargs={'pk': self.cluster.id},
                data={
                    'name': 'Attribute updated',
                    'description': 'The description updated',
                }
            ),
            TestingGetUIViews(
                url='resource_tracker_v2:resourcegroup_delete',
                perm_str='resource_tracker_v2.delete_resourcegroup',
                url_kwargs={'pk': self.cluster.id}
            ),
            TestingPostUIViews(
                url='resource_tracker_v2:resourcegroup_delete',
                perm_str='resource_tracker_v2.delete_resourcegroup',
                url_kwargs={'pk': self.cluster.id},

            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_transformer_views(self):
        self.vcpu_from_core_transformer.delete()
        testing_view_list = [
            TestingGetUIViews(
                url='resource_tracker_v2:ajax_load_attribute',
                perm_str='resource_tracker_v2.list_transformer',
                data={
                    'current_resource_group_id': self.single_vms.id,
                    'target_resource_group_id': self.cluster.id
                }
            ),
            TestingGetUIViews(
                url='resource_tracker_v2:transformer_list',
                perm_str='resource_tracker_v2.list_transformer',
                url_kwargs={'resource_group_id': self.single_vms.id}
            ),
            TestingGetUIViews(
                url='resource_tracker_v2:transformer_create',
                perm_str='resource_tracker_v2.add_transformer',
                url_kwargs={'resource_group_id': self.single_vms.id}
            ),
            TestingPostUIViews(
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
            TestingGetUIViews(
                url='resource_tracker_v2:transformer_edit',
                perm_str='resource_tracker_v2.change_transformer',
                url_kwargs={'resource_group_id': self.single_vms.id, 'attribute_id': self.vcpu_attribute.id}
            ),
            TestingPostUIViews(
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
            TestingGetUIViews(
                url='resource_tracker_v2:transformer_delete',
                perm_str='resource_tracker_v2.delete_transformer',
                url_kwargs={'resource_group_id': self.single_vms.id, 'attribute_id': self.vcpu_attribute.id}
            ),
            TestingPostUIViews(
                url='resource_tracker_v2:transformer_delete',
                perm_str='resource_tracker_v2.delete_transformer',
                url_kwargs={'resource_group_id': self.single_vms.id, 'attribute_id': self.vcpu_attribute.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_resource_views(self):
        testing_view_list = [
            TestingGetUIViews(
                url='resource_tracker_v2:resource_list',
                perm_str='resource_tracker_v2.list_resource',
                url_kwargs={'resource_group_id': self.single_vms.id}
            ),
            TestingGetUIViews(
                url='resource_tracker_v2:resource_create',
                perm_str='resource_tracker_v2.add_resource',
                url_kwargs={'resource_group_id': self.single_vms.id}
            ),
            TestingPostUIViews(
                url='resource_tracker_v2:resource_create',
                perm_str='resource_tracker_v2.add_resource',
                url_kwargs={'resource_group_id': self.single_vms.id},
                data={
                    'name': 'vm3',
                    'service_catalog_instance': '',
                    'is_deleted_on_instance_deletion': True,
                    'resource_group': self.single_vms.id
                }
            ),
            TestingGetUIViews(
                url='resource_tracker_v2:resource_edit',
                perm_str='resource_tracker_v2.change_resource',
                url_kwargs={'resource_group_id': self.single_vms.id, 'pk': self.vm1.id}
            ),
            TestingPostUIViews(
                url='resource_tracker_v2:resource_edit',
                perm_str='resource_tracker_v2.change_resource',
                url_kwargs={'resource_group_id': self.single_vms.id, 'pk': self.vm1.id},
                data={
                    'name': 'vm updated',
                    'service_catalog_instance': '',
                    'is_deleted_on_instance_deletion': True,
                    'resource_group': self.single_vms.id
                }
            ),
            TestingGetUIViews(
                url='resource_tracker_v2:resource_move',
                perm_str='resource_tracker_v2.change_resource',
                url_kwargs={'resource_group_id': self.single_vms.id, 'pk': self.vm1.id}
            ),
            TestingPostUIViews(
                url='resource_tracker_v2:resource_move',
                perm_str='resource_tracker_v2.change_resource',
                url_kwargs={'resource_group_id': self.single_vms.id, 'pk': self.vm1.id},
                data={
                    'resource_group': self.cluster.id
                }
            ),
            TestingGetUIViews(
                url='resource_tracker_v2:resource_delete',
                perm_str='resource_tracker_v2.delete_resource',
                url_kwargs={'resource_group_id': self.single_vms.id, 'pk': self.vm1.id}
            ),
            TestingPostUIViews(
                url='resource_tracker_v2:resource_delete',
                perm_str='resource_tracker_v2.delete_resource',
                url_kwargs={'resource_group_id': self.single_vms.id, 'pk': self.vm1.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_resource_views_bulk_delete(self):
        testing_view_list = [

            TestingPostUIViews(
                url='resource_tracker_v2:resource_bulk_delete_confirm',
                perm_str='resource_tracker_v2.delete_resource',
                url_kwargs={'resource_group_id': self.single_vms.id},
                data={
                    'selection': [resource.id for resource in self.single_vms.resources.all()]

                },
                expected_status_code=200
            ),
            TestingPostUIViews(
                url='resource_tracker_v2:resource_bulk_delete',
                perm_str='resource_tracker_v2.delete_resource',
                url_kwargs={'resource_group_id': self.single_vms.id},
                data={
                    'selection': [resource.id for resource in self.single_vms.resources.all()]

                }
            )
        ]

        self.run_permissions_tests(testing_view_list)
