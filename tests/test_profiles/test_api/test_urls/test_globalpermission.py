from profiles.models import Role, Permission
from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView, \
    TestingPatchContextView, TestingPutContextView, TestingDeleteContextView
from tests.test_profiles.base.base_test_profile import BaseTestProfileAPI


class TestProfilesGlobalPermissionPermissionsEndpoint(BaseTestProfileAPI, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.global_permission.add_user_in_role(self.standard_user, self.empty_role)

    def test_globalpermission_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_globalpermission_details',
                perm_str='profiles.view_globalpermission',
            ),
            TestingPutContextView(
                url='api_globalpermission_details',
                perm_str='profiles.change_globalpermission',
                data={
                    'roles': [],
                    'default_permissions': []
                },
            ),
            TestingPatchContextView(
                url='api_globalpermission_details',
                perm_str='profiles.change_globalpermission',
                data={
                    'default_permissions': []
                },
            ),
            TestingGetContextView(
                url='api_globalpermission_rbac_create',
                perm_str='profiles.view_users_globalpermission',
                url_kwargs={'scope_id': self.global_permission.id}
            ),
            TestingPostContextView(
                url='api_globalpermission_rbac_create',
                perm_str='profiles.add_users_globalpermission',
                url_kwargs={'scope_id': self.global_permission.id},
                data={'users': [self.standard_user.id], 'roles': [self.empty_role.id]}
            ),
            TestingDeleteContextView(
                url='api_globalpermission_rbac_delete',
                perm_str='profiles.delete_users_globalpermission',
                url_kwargs={
                    'scope_id': self.global_permission.id,
                    'user_id': self.standard_user.id,
                    'role_id': self.empty_role.id
                },
            ),
            TestingDeleteContextView(
                url='api_globalpermission_user_delete',
                perm_str='profiles.delete_users_globalpermission',
                url_kwargs={
                    'scope_id': self.global_permission.id,
                    'user_id': self.standard_user.id,
                },
            )
        ]
        self.run_permissions_tests(testing_view_list)
