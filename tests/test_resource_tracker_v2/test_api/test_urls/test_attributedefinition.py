from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView, \
    TestingPatchContextView, TestingPutContextView, TestingDeleteContextView
from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2API


class TestResourceTrackerV2AttributeDefinitionPermissionsEndpoint(BaseTestResourceTrackerV2API, TestPermissionEndpoint):
    def test_attributedefinition_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_attributedefinition_list_create',
                perm_str='resource_tracker_v2.list_attributedefinition',
            ),
            TestingPostContextView(
                url='api_attributedefinition_list_create',
                perm_str='resource_tracker_v2.add_attributedefinition',
                data={
                    'name': 'New attribute',
                    'description': 'The description',
                }
            ),
            TestingGetContextView(
                url='api_attributedefinition_details',
                perm_str='resource_tracker_v2.view_attributedefinition',
                url_kwargs={'pk': self.core_attribute.id}
            ),
            TestingPutContextView(
                url='api_attributedefinition_details',
                perm_str='resource_tracker_v2.change_attributedefinition',
                data={
                    'name': 'Attribute PUT',
                    'description': 'The description',
                },
                url_kwargs={'pk': self.core_attribute.id}
            ),
            TestingPatchContextView(
                url='api_attributedefinition_details',
                perm_str='resource_tracker_v2.change_attributedefinition',
                data={
                    'name': 'Attribute PATCH',
                },
                url_kwargs={'pk': self.core_attribute.id}
            ),
            TestingDeleteContextView(
                url='api_attributedefinition_details',
                perm_str='resource_tracker_v2.delete_attributedefinition',
                url_kwargs={'pk': self.core_attribute.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)
