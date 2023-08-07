from profiles.models.squest_permission import Permission

from profiles.models import Organization, Role
from tests.test_profiles.base.base_test_profile import BaseTestProfile
from tests.views import TestingGetUIViews, TestingPostUIViews, TestPermissionUIViews


class TestProfilesPermissionsViews(BaseTestProfile, TestPermissionUIViews):

    # URLs at the beginning of urls.py are personal and are tested elsewhere

    def test_user_views(self):
        testing_view_list = [
            # TODO: to be tested when User has been replaced by SquestUser (list_user permission not defined)
            # TestingGetUIViews(
            #     url='profiles:user_list',
            #     perm_str='auth.list_user',
            # ),
            TestingGetUIViews(
                url='profiles:user_details',
                perm_str='auth.view_user',
                url_kwargs={'pk': self.standard_user.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_globalpermission(self):
        testing_view_list = [
            TestingGetUIViews(
                url='profiles:globalpermission_rbac',
                perm_str='profiles.view_users_globalpermission',
            ),
            TestingGetUIViews(
                url='profiles:globalpermission_default_permissions',
                perm_str='profiles.view_globalpermission',
            ),
            TestingGetUIViews(
                url='profiles:globalpermission_edit',
                perm_str='profiles.change_globalpermission',
            ),
            TestingPostUIViews(
                url='profiles:globalpermission_edit',
                perm_str='profiles.change_globalpermission',
                data={'user_permission': [
                    Permission.objects.filter(content_type__app_label='service_catalog').first().id]}
            ),
            TestingGetUIViews(
                url='profiles:globalpermission_rbac_create',
                perm_str='profiles.add_users_globalpermission',
                url_kwargs={'scope_id': self.global_permission.id}
            ),
            TestingPostUIViews(
                url='profiles:globalpermission_rbac_create',
                perm_str='profiles.add_users_globalpermission',
                url_kwargs={'scope_id': self.global_permission.id},
                data={'users': self.standard_user.id, 'roles': self.empty_role.id}
            ),
            TestingPostUIViews(
                url='profiles:globalpermission_rbac_delete',
                perm_str='profiles.delete_users_globalpermission',
                url_kwargs={
                    'pk': self.global_permission.id,
                    'user_id': self.testing_user.id,
                    'role_id': self.empty_role.id
                },
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_organization_views(self):
        # organization delete is protected when organization have instances
        organization_to_delete = Organization.objects.create(name="To delete")
        testing_view_list = [
            TestingGetUIViews(
                url='profiles:organization_list',
                perm_str='profiles.list_organization',
            ),
            TestingGetUIViews(
                url='profiles:organization_create',
                perm_str='profiles.add_organization',
            ),
            TestingPostUIViews(
                url='profiles:organization_create',
                perm_str='profiles.add_organization',
                data={
                    'name': 'New organization',
                    'description': 'The description',
                    'roles': []
                }
            ),
            TestingGetUIViews(
                url='profiles:organization_details',
                perm_str='profiles.view_organization',
                url_kwargs={'pk': self.test_quota_scope_org.id}
            ),
            TestingGetUIViews(
                url='profiles:organization_edit',
                perm_str='profiles.change_organization',
                url_kwargs={'pk': self.test_quota_scope_org.id}
            ),
            TestingPostUIViews(
                url='profiles:organization_edit',
                perm_str='profiles.change_organization',
                url_kwargs={'pk': self.test_quota_scope_org.id},
                data={
                    'name': 'Organization updated',
                    'description': 'The description updated',
                    'roles': []
                }
            ),
            TestingGetUIViews(
                url='profiles:organization_rbac_create',
                perm_str='profiles.add_users_organization',
                url_kwargs={'scope_id': self.test_quota_scope_org.id}
            ),
            TestingPostUIViews(
                url='profiles:organization_rbac_create',
                perm_str='profiles.add_users_organization',
                url_kwargs={'scope_id': self.test_quota_scope_org.id},
                data={'users': self.standard_user.id, 'roles': self.empty_role.id}
            ),
            TestingPostUIViews(
                url='profiles:organization_rbac_delete',
                perm_str='profiles.delete_users_organization',
                url_kwargs={
                    'pk': self.test_quota_scope_org.id,
                    'user_id': self.standard_user.id,
                    'role_id': self.team_member_role.id
                },
            ),
            TestingGetUIViews(
                url='profiles:organization_delete',
                perm_str='profiles.delete_organization',
                url_kwargs={'pk': organization_to_delete.id}
            ),
            TestingPostUIViews(
                url='profiles:organization_delete',
                perm_str='profiles.delete_organization',
                url_kwargs={'pk': organization_to_delete.id},
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_team_views(self):
        # A permission to add a team in organization 2 must be defined for edit test
        add_team_role = Role.objects.create(name="Add team role")
        add_team_role.permissions.add(Permission.objects.get(content_type__app_label='profiles', codename='add_team'))
        self.test_quota_scope_org2.add_user_in_role(self.testing_user, add_team_role)
        testing_view_list = [
            TestingGetUIViews(
                url='profiles:team_list',
                perm_str='profiles.list_team',
            ),
            TestingPostUIViews(
                url='profiles:team_create',
                perm_str='profiles.add_team',
                data={
                    'name': 'New team',
                    'description': 'The description',
                    'roles': [],
                    'org': self.test_quota_scope_org.id
                },
                expected_not_allowed_status_code=200
            ),
            TestingGetUIViews(
                url='profiles:team_details',
                perm_str='profiles.view_team',
                url_kwargs={'pk': self.test_quota_scope_team.id}
            ),
            TestingGetUIViews(
                url='profiles:team_rbac_create',
                perm_str='profiles.add_users_team',
                url_kwargs={'scope_id': self.test_quota_scope_team.id}
            ),
            TestingPostUIViews(
                url='profiles:team_rbac_create',
                perm_str='profiles.add_users_team',
                url_kwargs={'scope_id': self.test_quota_scope_team.id},
                data={'users': self.standard_user.id, 'roles': self.empty_role.id}
            ),
            TestingPostUIViews(
                url='profiles:team_rbac_delete',
                perm_str='profiles.delete_users_team',
                url_kwargs={
                    'pk': self.test_quota_scope_team.id,
                    'user_id': self.standard_user.id,
                    'role_id': self.team_member_role.id
                },
            ),
            TestingGetUIViews(
                url='profiles:team_delete',
                perm_str='profiles.delete_team',
                url_kwargs={'pk': self.test_quota_scope_team.id}
            ),
            TestingGetUIViews(
                url='profiles:team_edit',
                perm_str='profiles.change_team',
                url_kwargs={'pk': self.test_quota_scope_team.id}
            ),
            TestingPostUIViews(
                url='profiles:team_edit',
                perm_str='profiles.change_team',
                url_kwargs={'pk': self.test_quota_scope_team.id},
                data={
                    'name': 'Organization updated',
                    'description': 'The description updated',
                    'roles': [],
                    'org': self.test_quota_scope_org2.id
                }
            ),
            TestingPostUIViews(
                url='profiles:team_delete',
                perm_str='profiles.delete_team',
                url_kwargs={'pk': self.test_quota_scope_team.id},
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_permission_views(self):
        permission = Permission.objects.filter(content_type__app_label='service_catalog').first()
        testing_view_list = [
            TestingGetUIViews(
                url='profiles:permission_list',
                perm_str='profiles.list_permission',
            ),
            TestingGetUIViews(
                url='profiles:permission_create',
                perm_str='profiles.add_permission',
            ),
            TestingPostUIViews(
                url='profiles:permission_create',
                perm_str='profiles.add_permission',
                data={
                    'name': 'New permission',
                    'codename': 'the_code_name',
                    'content_type': permission.content_type.id
                }
            ),
            TestingGetUIViews(
                url='profiles:permission_edit',
                perm_str='profiles.change_permission',
                url_kwargs={'pk': permission.id}
            ),
            TestingPostUIViews(
                url='profiles:permission_edit',
                perm_str='profiles.change_permission',
                url_kwargs={'pk': permission.id},
                data={
                    'name': 'Permission updated',
                    'codename': 'the_code_name_updated',
                    'content_type': permission.content_type.id
                }
            ),
            TestingGetUIViews(
                url='profiles:permission_delete',
                perm_str='profiles.delete_permission',
                url_kwargs={'pk': permission.id}
            ),
            TestingPostUIViews(
                url='profiles:permission_delete',
                perm_str='profiles.delete_permission',
                url_kwargs={'pk': permission.id},

            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_role_views(self):
        testing_view_list = [
            TestingGetUIViews(
                url='profiles:role_list',
                perm_str='profiles.list_role',
            ),
            TestingGetUIViews(
                url='profiles:role_details',
                perm_str='profiles.view_role',
                url_kwargs={'pk': self.organization_admin_role.id}
            ),
            TestingGetUIViews(
                url='profiles:role_create',
                perm_str='profiles.add_role',
            ),
            TestingPostUIViews(
                url='profiles:role_create',
                perm_str='profiles.add_role',
                data={
                    'name': 'New role',
                    'description': 'The description',
                    'permissions': []
                }
            ),
            TestingGetUIViews(
                url='profiles:role_edit',
                perm_str='profiles.change_role',
                url_kwargs={'pk': self.organization_admin_role.id}
            ),
            TestingPostUIViews(
                url='profiles:role_edit',
                perm_str='profiles.change_role',
                url_kwargs={'pk': self.organization_admin_role.id},
                data={
                    'name': 'Role updated',
                    'description': 'The description updated',
                    'permissions': []
                }
            ),
            TestingGetUIViews(
                url='profiles:role_delete',
                perm_str='profiles.delete_role',
                url_kwargs={'pk': self.organization_admin_role.id}
            ),
            TestingPostUIViews(
                url='profiles:role_delete',
                perm_str='profiles.delete_role',
                url_kwargs={'pk': self.organization_admin_role.id},

            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_quota_views(self):
        testing_view_list = [
            TestingGetUIViews(
                url='profiles:quota_list',
                perm_str='profiles.list_quota'
            ),
            TestingGetUIViews(
                url='profiles:quota_details',
                perm_str='profiles.view_quota',
                url_kwargs={'scope_id': self.test_org.id, 'quota_id': self.test_quota_org.id}
            ),
            TestingGetUIViews(
                url='profiles:organization_quota_edit',
                perm_str='profiles.change_quota',
                url_kwargs={'scope_id': self.test_org.id}
            ),
            TestingPostUIViews(
                url='profiles:organization_quota_edit',
                perm_str='profiles.change_quota',
                url_kwargs={'scope_id': self.test_org.id},
                data={
                    f"attribute_definition_{self.cpu_attribute.id}": 100,
                    f"attribute_definition_{self.other_attribute.id}": 50
                }
            ),
            TestingGetUIViews(
                url='profiles:team_quota_edit',
                perm_str='profiles.change_quota',
                url_kwargs={'scope_id': self.test_quota_scope_team.id}
            ),
            TestingPostUIViews(
                url='profiles:team_quota_edit',
                perm_str='profiles.change_quota',
                url_kwargs={'scope_id': self.test_quota_scope_team.id},
                data={
                    f"attribute_definition_{self.cpu_attribute.id}": 100,
                    f"attribute_definition_{self.other_attribute.id}": 50
                }
            )
        ]
        self.run_permissions_tests(testing_view_list)
