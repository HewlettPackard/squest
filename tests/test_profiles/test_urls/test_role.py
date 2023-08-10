from tests.test_profiles.base.base_test_profile import BaseTestProfile
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestProfilesRolePermissionsViews(BaseTestProfile, TestPermissionEndpoint):
    def test_role_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='profiles:role_list',
                perm_str='profiles.list_role',
            ),
            TestingGetContextView(
                url='profiles:role_details',
                perm_str='profiles.view_role',
                url_kwargs={'pk': self.organization_admin_role.id}
            ),
            TestingGetContextView(
                url='profiles:role_create',
                perm_str='profiles.add_role',
            ),
            TestingPostContextView(
                url='profiles:role_create',
                perm_str='profiles.add_role',
                data={
                    'name': 'New role',
                    'description': 'The description',
                    'permissions': []
                }
            ),
            TestingGetContextView(
                url='profiles:role_edit',
                perm_str='profiles.change_role',
                url_kwargs={'pk': self.organization_admin_role.id}
            ),
            TestingPostContextView(
                url='profiles:role_edit',
                perm_str='profiles.change_role',
                url_kwargs={'pk': self.organization_admin_role.id},
                data={
                    'name': 'Role updated',
                    'description': 'The description updated',
                    'permissions': []
                }
            ),
            TestingGetContextView(
                url='profiles:role_delete',
                perm_str='profiles.delete_role',
                url_kwargs={'pk': self.organization_admin_role.id}
            ),
            TestingPostContextView(
                url='profiles:role_delete',
                perm_str='profiles.delete_role',
                url_kwargs={'pk': self.organization_admin_role.id},

            )
        ]
        self.run_permissions_tests(testing_view_list)
