from resource_tracker_v2.models import AttributeGroup
from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestResourceTrackerV2AttributeGroupPermissionsViews(BaseTestResourceTrackerV2, TestPermissionEndpoint):

    def setUp(self):
        super().setUp()
        self.vm_attributes = AttributeGroup.objects.create(
            name='VM',
            description='The attributes for VM'
        )

    def test_attributegroup_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='resource_tracker_v2:attributegroup_list',
                perm_str='resource_tracker_v2.list_attributegroup',
            ),
            TestingGetContextView(
                url='resource_tracker_v2:attributegroup_details',
                perm_str='resource_tracker_v2.view_attributegroup',
                url_kwargs={'pk': self.vm_attributes.id}
            ),
            TestingGetContextView(
                url='resource_tracker_v2:attributegroup_create',
                perm_str='resource_tracker_v2.add_attributegroup',
            ),
            TestingPostContextView(
                url='resource_tracker_v2:attributegroup_create',
                perm_str='resource_tracker_v2.add_attributegroup',
                data={
                    'name': 'New attribute',
                    'description': 'The description',
                }
            ),
            TestingGetContextView(
                url='resource_tracker_v2:attributegroup_edit',
                perm_str='resource_tracker_v2.change_attributegroup',
                url_kwargs={'pk': self.vm_attributes.id}
            ),
            TestingPostContextView(
                url='resource_tracker_v2:attributegroup_edit',
                perm_str='resource_tracker_v2.change_attributegroup',
                url_kwargs={'pk': self.vm_attributes.id},
                data={
                    'name': 'Attribute updated',
                    'description': 'The description updated',
                }
            ),
            TestingGetContextView(
                url='resource_tracker_v2:attributegroup_delete',
                perm_str='resource_tracker_v2.delete_attributegroup',
                url_kwargs={'pk': self.vm_attributes.id}
            ),
            TestingPostContextView(
                url='resource_tracker_v2:attributegroup_delete',
                perm_str='resource_tracker_v2.delete_attributegroup',
                url_kwargs={'pk': self.vm_attributes.id},

            )
        ]
        self.run_permissions_tests(testing_view_list)
