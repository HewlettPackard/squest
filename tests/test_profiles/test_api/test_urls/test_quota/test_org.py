from profiles.models import Quota
from resource_tracker_v2.models import AttributeDefinition
from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView, \
    TestingPatchContextView, TestingPutContextView, TestingDeleteContextView
from tests.test_profiles.base.base_test_profile import BaseTestProfileAPI


class TestProfilesQuotaOrganizationPermissionsEndpoint(BaseTestProfileAPI, TestPermissionEndpoint):
    def test_quota_organization_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_quota_list_create',
                perm_str_list=['profiles.list_quota'],
            ),
            TestingPostContextView(
                url='api_quota_list_create',
                perm_str_list=['profiles.add_quota'],
                data={
                    'scope': self.test_quota_scope_org.id,
                    'attribute_definition': self.cpu_attribute.id,
                    'limit': 500
                }
            ),
            TestingGetContextView(
                url='api_quota_details',
                perm_str_list=['profiles.view_quota'],
                url_kwargs={'pk': self.test_quota_org.id}
            ),
            TestingPutContextView(
                url='api_quota_details',
                perm_str_list=['profiles.change_organization_quota'],
                data={
                    'scope': self.test_org.id,
                    'attribute_definition': self.cpu_attribute.id,
                    'limit': 5000
                },
                url_kwargs={'pk': self.test_quota_org.id}
            ),
            TestingPatchContextView(
                url='api_quota_details',
                perm_str_list=['profiles.change_organization_quota'],
                data={
                    'limit': 100
                },
                url_kwargs={'pk': self.test_quota_org.id}
            ),
            TestingDeleteContextView(
                url='api_quota_details',
                perm_str_list=['profiles.delete_quota'],
                url_kwargs={'pk': self.test_quota_org.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)