from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView, \
    TestingPatchContextView, TestingPutContextView, TestingDeleteContextView
from tests.test_profiles.base.base_test_profile import BaseTestProfileAPI


class TestProfilesRolePermissionsEndpoint(BaseTestProfileAPI, TestPermissionEndpoint):
    def test_role_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_role_list_create',
                perm_str='profiles.list_role',
            ),
            TestingPostContextView(
                url='api_role_list_create',
                perm_str='profiles.add_role',
                data={
                    'name': 'New role',
                    'description': 'The description',
                    'org': self.test_quota_scope_org.id
                }
            ),
            TestingGetContextView(
                url='api_role_details',
                perm_str='profiles.view_role',
                url_kwargs={'pk': self.organization_admin_role.id}
            ),
            TestingPutContextView(
                url='api_role_details',
                perm_str='profiles.change_role',
                data={
                    'name': 'Role put',
                    'description': 'The description',
                    'roles': [],
                    'org': self.test_quota_scope_org.id
                },
                url_kwargs={'pk': self.organization_admin_role.id}
            ),
            TestingPatchContextView(
                url='api_role_details',
                perm_str='profiles.change_role',
                data={
                    'description': "new description patch"
                },
                url_kwargs={'pk': self.organization_admin_role.id}
            ),
            TestingDeleteContextView(
                url='api_role_details',
                perm_str='profiles.delete_role',
                url_kwargs={'pk': self.organization_admin_role.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)
