from profiles.models import Role, Permission
from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView, \
    TestingPatchContextView, TestingPutContextView, TestingDeleteContextView
from tests.test_profiles.base.base_test_profile import BaseTestProfileAPI


class TestProfilesTeamPermissionsEndpoint(BaseTestProfileAPI, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        # A permission to add a team in organization 2 must be defined for edit test
        add_team_role = Role.objects.create(name="Add team role")
        add_team_role.permissions.add(Permission.objects.get(content_type__app_label='profiles', codename='add_team'))
        self.test_quota_scope_org2.add_user_in_role(self.testing_user, add_team_role)

        self.test_quota_scope_team.org.add_user_in_role(self.standard_user, self.empty_role)
        self.test_quota_scope_team.add_user_in_role(self.standard_user, self.empty_role)

    def test_team_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_team_list_create',
                perm_str='profiles.list_team',
            ),
            TestingPostContextView(
                url='api_team_list_create',
                perm_str='profiles.add_team',
                data={
                    'name': 'New team',
                    'description': 'The description',
                    'org': self.test_quota_scope_org.id
                }
            ),
            TestingGetContextView(
                url='api_team_details',
                perm_str='profiles.view_team',
                url_kwargs={'pk': self.test_quota_scope_team.id}
            ),
            TestingPutContextView(
                url='api_team_details',
                perm_str='profiles.change_team',
                data={
                    'name': 'Team put',
                    'description': 'The description',
                    'roles': [],
                    'org': self.test_quota_scope_org.id
                },
                url_kwargs={'pk': self.test_quota_scope_team.id}
            ),
            TestingPatchContextView(
                url='api_team_details',
                perm_str='profiles.change_team',
                data={
                    'description': "new description patch"
                },
                url_kwargs={'pk': self.test_quota_scope_team.id}
            ),
            TestingPostContextView(
                url='api_team_rbac_create',
                perm_str='profiles.add_users_team',
                url_kwargs={'scope_id': self.test_quota_scope_team.id},
                data={'users': [self.standard_user.id], 'roles': [self.empty_role.id]}
            ),
            TestingDeleteContextView(
                url='api_team_rbac_delete',
                perm_str='profiles.delete_users_team',
                url_kwargs={
                    'scope_id': self.test_quota_scope_team.id,
                    'user_id': self.standard_user.id,
                    'role_id': self.team_member_role.id
                },
            ),
            TestingDeleteContextView(
                url='api_team_user_delete',
                perm_str='profiles.delete_users_team',
                url_kwargs={
                    'scope_id': self.test_quota_scope_team.id,
                    'user_id': self.standard_user.id,
                },
            ),
            TestingDeleteContextView(
                url='api_team_details',
                perm_str='profiles.delete_team',
                url_kwargs={'pk': self.test_quota_scope_team.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)
