from profiles.models import Role, Permission
from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView, \
    TestingPatchContextView, TestingPutContextView, TestingDeleteContextView
from tests.test_profiles.base.base_test_profile import BaseTestProfileAPI


class TestProfilesGlobalScopePermissionsEndpoint(BaseTestProfileAPI, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.global_scope.add_user_in_role(self.standard_user, self.empty_role)

    def test_globalscope_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_globalscope_details',
                perm_str_list=['profiles.view_globalscope'],
            ),
            TestingPutContextView(
                url='api_globalscope_details',
                perm_str_list=['profiles.change_globalscope'],
                data={
                    'roles': [],
                    'global_permissions': []
                },
            ),
            TestingPatchContextView(
                url='api_globalscope_details',
                perm_str_list=['profiles.change_globalscope'],
                data={
                    'global_permissions': []
                },
            ),
            TestingGetContextView(
                url='api_globalscope_rbac_create',
                perm_str_list=['profiles.view_users_globalscope'],
                url_kwargs={'scope_id': self.global_scope.id}
            ),
            TestingPostContextView(
                url='api_globalscope_rbac_create',
                perm_str_list=['profiles.add_users_globalscope'],
                url_kwargs={'scope_id': self.global_scope.id},
                data={'users': [self.standard_user.id], 'roles': [self.empty_role.id]}
            ),
            TestingDeleteContextView(
                url='api_globalscope_rbac_delete',
                perm_str_list=['profiles.delete_users_globalscope'],
                url_kwargs={
                    'scope_id': self.global_scope.id,
                    'user_id': self.standard_user.id,
                    'role_id': self.empty_role.id
                },
            ),
            TestingDeleteContextView(
                url='api_globalscope_user_delete',
                perm_str_list=['profiles.delete_users_globalscope'],
                url_kwargs={
                    'scope_id': self.global_scope.id,
                    'user_id': self.standard_user.id,
                },
            )
        ]
        self.run_permissions_tests(testing_view_list)