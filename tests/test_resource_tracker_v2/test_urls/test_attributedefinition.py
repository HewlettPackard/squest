from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestResourceTrackerV2AttributeDefinitionPermissionsViews(BaseTestResourceTrackerV2, TestPermissionEndpoint):
    def test_attributedefinition_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='resource_tracker_v2:attributedefinition_list',
                perm_str_list=['resource_tracker_v2.list_attributedefinition'],
            ),
            TestingGetContextView(
                url='resource_tracker_v2:attributedefinition_details',
                perm_str_list=['resource_tracker_v2.view_attributedefinition'],
                url_kwargs={'pk': self.core_attribute.id}
            ),
            TestingGetContextView(
                url='resource_tracker_v2:attributedefinition_create',
                perm_str_list=['resource_tracker_v2.add_attributedefinition'],
            ),
            TestingPostContextView(
                url='resource_tracker_v2:attributedefinition_create',
                perm_str_list=['resource_tracker_v2.add_attributedefinition'],
                data={
                    'name': 'New attribute',
                    'description': 'The description',
                }
            ),
            TestingGetContextView(
                url='resource_tracker_v2:attributedefinition_edit',
                perm_str_list=['resource_tracker_v2.change_attributedefinition'],
                url_kwargs={'pk': self.core_attribute.id}
            ),
            TestingPostContextView(
                url='resource_tracker_v2:attributedefinition_edit',
                perm_str_list=['resource_tracker_v2.change_attributedefinition'],
                url_kwargs={'pk': self.core_attribute.id},
                data={
                    'name': 'Attribute updated',
                    'description': 'The description updated',
                }
            ),
            TestingGetContextView(
                url='resource_tracker_v2:attributedefinition_delete',
                perm_str_list=['resource_tracker_v2.delete_attributedefinition'],
                url_kwargs={'pk': self.core_attribute.id}
            ),
            TestingPostContextView(
                url='resource_tracker_v2:attributedefinition_delete',
                perm_str_list=['resource_tracker_v2.delete_attributedefinition'],
                url_kwargs={'pk': self.core_attribute.id},

            )
        ]
        self.run_permissions_tests(testing_view_list)