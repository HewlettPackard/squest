from profiles.models.squest_permission import Permission

from profiles.models import Role
from tests.test_profiles.base.base_test_profile import BaseTestProfile
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestProfilesTeamPermissionsViews(BaseTestProfile, TestPermissionEndpoint):
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
                url='profiles:team_list',
                perm_str_list=['profiles.list_team'],
            ),
            TestingPostContextView(
                url='profiles:team_create',
                perm_str_list=['profiles.add_team'],
                data={
                    'name': 'New team',
                    'description': 'The description',
                    'roles': [],
                    'org': self.test_quota_scope_org.id
                },
                expected_not_allowed_status_code=200
            ),
            TestingGetContextView(
                url='profiles:team_details',
                perm_str_list=['profiles.view_team'],
                url_kwargs={'pk': self.test_quota_scope_team.id}
            ),
            TestingGetContextView(
                url='profiles:team_rbac_create',
                perm_str_list=['profiles.add_users_team'],
                url_kwargs={'scope_id': self.test_quota_scope_team.id}
            ),
            TestingPostContextView(
                url='profiles:team_rbac_create',
                perm_str_list=['profiles.add_users_team'],
                url_kwargs={'scope_id': self.test_quota_scope_team.id},
                data={'users': self.standard_user.id, 'roles': self.empty_role.id}
            ),
            TestingPostContextView(
                url='profiles:team_rbac_delete',
                perm_str_list=['profiles.delete_users_team'],
                url_kwargs={
                    'pk': self.test_quota_scope_team.id,
                    'user_id': self.standard_user.id,
                    'role_id': self.team_member_role.id
                },
            ),
            TestingGetContextView(
                url='profiles:team_rbac_delete',
                perm_str_list=['profiles.delete_users_team'],
                url_kwargs={
                    'pk': self.test_quota_scope_team.id,
                    'user_id': self.standard_user.id,
                },
            ),
            TestingPostContextView(
                url='profiles:team_rbac_delete',
                perm_str_list=['profiles.delete_users_team'],
                url_kwargs={
                    'pk': self.test_quota_scope_team.id,
                    'user_id': self.standard_user.id,
                },
            ),
            TestingGetContextView(
                url='profiles:team_delete',
                perm_str_list=['profiles.delete_team'],
                url_kwargs={'pk': self.test_quota_scope_team.id}
            ),
            TestingGetContextView(
                url='profiles:team_edit',
                perm_str_list=['profiles.change_team'],
                url_kwargs={'pk': self.test_quota_scope_team.id}
            ),
            TestingPostContextView(
                url='profiles:team_edit',
                perm_str_list=['profiles.change_team'],
                url_kwargs={'pk': self.test_quota_scope_team.id},
                data={
                    'name': 'Organization updated',
                    'description': 'The description updated',
                    'roles': [],
                    'org': self.test_quota_scope_org2.id
                }
            ),
            TestingPostContextView(
                url='profiles:team_delete',
                perm_str_list=['profiles.delete_team'],
                url_kwargs={'pk': self.test_quota_scope_team.id},
            )
        ]
        self.run_permissions_tests(testing_view_list)