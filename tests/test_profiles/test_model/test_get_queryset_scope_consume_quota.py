from django.contrib.auth.models import User, Permission

from profiles.models import Team, Organization, GlobalPermission, Role, Scope

from tests.utils import TransactionTestUtils


class TestModelScopeGetQuerysetConsumeQuota(TransactionTestUtils):

    def setUp(self):
        super(TestModelScopeGetQuerysetConsumeQuota, self).setUp()
        self.user1 = User.objects.create_user('user1', 'user1@hpe.com', "password")
        self.user2 = User.objects.create_user('user2', 'user2@hpe.com', "password")
        self.user3 = User.objects.create_user('user3', 'user3@hpe.com', "password")
        self.superuser = User.objects.create_superuser("superuser")

        self.global_perm = GlobalPermission.load()
        self.empty_role = Role.objects.create(name="Empty role")
        self.permission_object = Permission.objects.get(content_type__app_label="profiles",
                                                        content_type__model="scope",
                                                        codename="consume_quota_scope")

    def _assert_can_consume_only_quota_qs(self, user, quota_qs):
        perm = "profiles.consume_quota_scope"
        self.assertQuerysetEqualID(Scope.get_queryset_for_user(user, perm), quota_qs)

    def _assert_cannot_consume_quota(self, user):
        perm = "profiles.consume_quota_scope"
        self.assertQuerysetEqualID(Scope.get_queryset_for_user(user, perm), Scope.objects.none())

    def test_get_queryset_organization_by_querying_scope_with_global_permission_role(self):
        """
        Test that we can consume all quota by querying Scope if permission is given in a GlobalPermission's role
        """

        # Only superuser can see
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_cannot_consume_quota(self.superuser)

        # Create role to view Scope
        role = Role.objects.create(name="View Scope")
        role.permissions.add(self.permission_object)

        # Assign role to view Scope to user1
        self.global_perm.add_user_in_role(self.user1, role)

        # Create a new organization
        org1 = Organization.objects.create(name="Scope #1")
        self.assertTrue(org1 in Organization.objects.all())
        self.assertEqual(Organization.objects.count(), 1)

        # Only user1 can see it
        self._assert_can_consume_only_quota_qs(self.user1, quota_qs=Scope.objects.filter(id__in=[org1.id]))
        self._assert_cannot_consume_quota(self.user2)
        self._assert_can_consume_only_quota_qs(self.superuser, quota_qs=Scope.objects.filter(id__in=[org1.id]))

        # Remove permission to user1
        self.global_perm.remove_user_in_role(self.user1, role)

        # Only superuser can see
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_can_consume_only_quota_qs(self.superuser, quota_qs=Scope.objects.filter(id__in=[org1.id]))

    def test_get_queryset_organization_by_querying_scope_with_global_permission__user_permissions(self):
        """
        Test that we can consume Organization quota by querying Scope if permission is given in a GlobalPermission's perm
        """

        # Only superuser can see
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_cannot_consume_quota(self.superuser)

        # Create Permission/Role_scope")

        # Assign permission to all users
        self.global_perm.user_permissions.add(self.permission_object)

        # Create a new organization
        org1 = Organization.objects.create(name="Organization #1")
        self.assertTrue(org1 in Organization.objects.all())
        self.assertEqual(Organization.objects.count(), 1)

        # Everyone can see it
        self._assert_can_consume_only_quota_qs(self.user1, quota_qs=Scope.objects.filter(id__in=[org1.id]))
        self._assert_can_consume_only_quota_qs(self.user2, quota_qs=Scope.objects.filter(id__in=[org1.id]))
        self._assert_can_consume_only_quota_qs(self.superuser, quota_qs=Scope.objects.filter(id__in=[org1.id]))

        # Remove permission to all users
        self.global_perm.user_permissions.remove(self.permission_object)

        # Only superuser can see
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_can_consume_only_quota_qs(self.superuser, quota_qs=Scope.objects.filter(id__in=[org1.id]))

    def test_get_queryset_team_by_querying_scope_with_global_permission_role(self):
        """
        Test that we can consume Team quota by querying Scope if permission is given in a GlobalPermission's role
        """
        # Only superuser can see
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_cannot_consume_quota(self.superuser)

        # Create Permission/Role
        role = Role.objects.create(name="View Team")
        role.permissions.add(self.permission_object)

        # Assign role to user1
        self.global_perm.add_user_in_role(self.user1, role)

        # Create a new organization/team
        org1 = Organization.objects.create(name="Organization #1")
        team1 = Team.objects.create(name="Team #1", org=org1)
        self.assertTrue(team1 in Team.objects.all())
        self.assertEqual(Team.objects.count(), 1)

        # user1 can see it
        self._assert_can_consume_only_quota_qs(self.user1, quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))
        self._assert_cannot_consume_quota(self.user2)
        self._assert_can_consume_only_quota_qs(self.superuser,
                                               quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))

        # Remove role to user1
        self.global_perm.remove_user_in_role(self.user1, role)

        # Only superuser can see
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_can_consume_only_quota_qs(self.superuser,
                                               quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))

    def test_get_queryset_team_by_querying_scope_with_global_permission__user_permissions(self):
        """
        Test that we can consume Team quota if permission is given in a GlobalPermission's perm
        """
        # Only superuser can see
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_cannot_consume_quota(self.superuser)

        # Create Permission/Role
        self.global_perm.user_permissions.add(self.permission_object)

        # Create a new organization/team
        org1 = Organization.objects.create(name="Organization #1")
        team1 = Team.objects.create(name="Team #1", org=org1)
        self.assertTrue(team1 in Team.objects.all())
        self.assertEqual(Team.objects.count(), 1)

        # Everyone can see it
        self._assert_can_consume_only_quota_qs(self.user1, quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))
        self._assert_can_consume_only_quota_qs(self.user2, quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))
        self._assert_can_consume_only_quota_qs(self.superuser,
                                               quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))

        # Remove role to everyone
        self.global_perm.user_permissions.remove(self.permission_object)

        # Only superuser can see
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_can_consume_only_quota_qs(self.superuser,
                                               quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))

    def test_get_queryset_organization_by_querying_scope_with_organization_role(self):
        """
        Test that we can consume Orga quotanization if permission is given in an Organization's role
        """

        # Only superuser can see
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_cannot_consume_quota(self.superuser)

        # Create Permission/Role
        role = Role.objects.create(name="View Organization")
        role.permissions.add(self.permission_object)

        # Create a new organization
        org1 = Organization.objects.create(name="Organization #1")
        self.assertTrue(org1 in Organization.objects.all())
        self.assertEqual(Organization.objects.count(), 1)

        # Only superuser can see it
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_can_consume_only_quota_qs(self.superuser, quota_qs=Scope.objects.filter(id__in=[org1.id]))

        # Assign role to user1
        org1.add_user_in_role(self.user1, role)

        # user1 can see it
        self._assert_can_consume_only_quota_qs(self.user1, quota_qs=Scope.objects.filter(id__in=[org1.id]))
        self._assert_cannot_consume_quota(self.user2)
        self._assert_can_consume_only_quota_qs(self.superuser, quota_qs=Scope.objects.filter(id__in=[org1.id]))

        # Remove role to user1
        org1.remove_user_in_role(self.user1, role)

        # Only superuser can see
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_can_consume_only_quota_qs(self.superuser, quota_qs=Scope.objects.filter(id__in=[org1.id]))

    def test_get_queryset_organization_by_querying_scope_with_organization_default_role(self):
        """
        Test that we can consume Orga quotanization if permission is given in a Organization's default role
        """

        # Only superuser can see it
        self._assert_cannot_consume_quota(self.superuser)
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_cannot_consume_quota(self.user3)

        # Create a new organization
        org1 = Organization.objects.create(name="Organization #1")
        self.assertTrue(org1 in Organization.objects.all())
        self.assertEqual(Organization.objects.count(), 1)

        # Create Permission/Role
        role = Role.objects.create(name="View Organization")
        role.permissions.add(self.permission_object)

        # Add view org to all organization's user
        org1.roles.add(role)

        # No user in org1 so only superuser can see
        self._assert_can_consume_only_quota_qs(self.superuser, quota_qs=Scope.objects.filter(id__in=[org1.id]))
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_cannot_consume_quota(self.user3)

        # assign an empty role to user1 and user2
        org1.add_user_in_role(self.user1, self.empty_role)
        org1.add_user_in_role(self.user2, self.empty_role)

        # everyone can see except user3
        self._assert_can_consume_only_quota_qs(self.superuser, quota_qs=Scope.objects.filter(id__in=[org1.id]))
        self._assert_can_consume_only_quota_qs(self.user1, quota_qs=Scope.objects.filter(id__in=[org1.id]))
        self._assert_can_consume_only_quota_qs(self.user2, quota_qs=Scope.objects.filter(id__in=[org1.id]))
        self._assert_cannot_consume_quota(self.user3)

        # remove user2 from org
        org1.remove_user_in_role(self.user2, self.empty_role)

        # user1 is still in organization
        self._assert_can_consume_only_quota_qs(self.superuser, quota_qs=Scope.objects.filter(id__in=[org1.id]))
        self._assert_can_consume_only_quota_qs(self.user1, quota_qs=Scope.objects.filter(id__in=[org1.id]))
        self._assert_cannot_consume_quota(self.user2)
        self._assert_cannot_consume_quota(self.user3)

        # Remove view org to all organization's user
        org1.roles.remove(role)

        # only super can see
        self._assert_can_consume_only_quota_qs(self.superuser, quota_qs=Scope.objects.filter(id__in=[org1.id]))
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_cannot_consume_quota(self.user3)

    def test_get_queryset_team_by_querying_scope_with_organization_role(self):
        """
        Test that we can consume Team quota if permission is given in a Organization's role
        """

        # Only superuser can see
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_cannot_consume_quota(self.superuser)
        # Create Permission/Role
        role = Role.objects.create(name="View Team")
        role.permissions.add(self.permission_object)

        # Create a new organization
        org1 = Organization.objects.create(name="Organization #1")
        team1 = Team.objects.create(name="Team #1", org=org1)
        self.assertTrue(team1 in Team.objects.all())
        self.assertEqual(Team.objects.count(), 1)

        # Only superuser can see
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_can_consume_only_quota_qs(self.superuser,
                                               quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))

        # Assign role to user1
        org1.add_user_in_role(self.user1, role)

        # user1 can see it
        self._assert_can_consume_only_quota_qs(self.user1, quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))
        self._assert_cannot_consume_quota(self.user2)
        self._assert_can_consume_only_quota_qs(self.superuser,
                                               quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))

        # Remove role to user1
        org1.remove_user_in_role(self.user1, role)

        # Only superuser can see
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_can_consume_only_quota_qs(self.superuser,
                                               quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))

    def test_get_queryset_team_by_querying_scope_with_organization_default_role(self):
        """
        Test that we can consume Team quota if permission is given in a Organization's default role
        """
        # No instances
        self._assert_cannot_consume_quota(self.superuser)
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_cannot_consume_quota(self.user3)

        # Create a team/organization
        org1 = Organization.objects.create(name="Organization #1")
        team1 = Team.objects.create(name="Team #1", org=org1)
        self.assertTrue(team1 in Team.objects.all())
        self.assertEqual(Team.objects.count(), 1)

        # Add view org to all organization's user
        role = Role.objects.create(name="View Team")
        role.permissions.add(self.permission_object)

        # Assign role to the whole organization
        org1.roles.add(role)

        # No user in org1 so only superuser can see
        self._assert_can_consume_only_quota_qs(self.superuser,
                                               quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_cannot_consume_quota(self.user3)

        # assign an empty role to user1 and user2
        org1.add_user_in_role(self.user1, self.empty_role)
        org1.add_user_in_role(self.user2, self.empty_role)

        # everyone can see except user3
        self._assert_can_consume_only_quota_qs(self.superuser,
                                               quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))
        self._assert_can_consume_only_quota_qs(self.user1, quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))
        self._assert_can_consume_only_quota_qs(self.user2, quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))
        self._assert_cannot_consume_quota(self.user3)

        # remove user2 from org
        org1.remove_user_in_role(self.user2, self.empty_role)

        # user1 is still in organization
        self._assert_can_consume_only_quota_qs(self.superuser,
                                               quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))
        self._assert_can_consume_only_quota_qs(self.user1, quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))
        self._assert_cannot_consume_quota(self.user2)
        self._assert_cannot_consume_quota(self.user3)

        # Remove view org to all organization's user
        org1.roles.remove(role)

        # only super can see
        self._assert_can_consume_only_quota_qs(self.superuser,
                                               quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_cannot_consume_quota(self.user3)

    def test_get_queryset_team_by_querying_scope_with_team_role(self):
        """
        Test that we can consume Team quota if permission is given in a Team's role
        """

        # Only superuser can see
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_cannot_consume_quota(self.superuser)

        # Create Permission/Role
        role = Role.objects.create(name="View Team")
        role.permissions.add(self.permission_object)

        # Create a new organization
        org1 = Organization.objects.create(name="Organization #1")
        team1 = Team.objects.create(name="Team #1", org=org1)
        self.assertTrue(team1 in Team.objects.all())
        self.assertEqual(Team.objects.count(), 1)

        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_can_consume_only_quota_qs(self.superuser,
                                               quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))

        # Assign role to user1
        org1.add_user_in_role(self.user1, self.empty_role)
        team1.add_user_in_role(self.user1, role)

        # user1 can see it
        self._assert_can_consume_only_quota_qs(self.user1, quota_qs=Scope.objects.filter(id__in=[team1.id]))
        self._assert_cannot_consume_quota(self.user2)
        self._assert_can_consume_only_quota_qs(self.superuser,
                                               quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))

        # Remove role to user1
        team1.remove_user_in_role(self.user1, role)

        # Only superuser can see it
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_can_consume_only_quota_qs(self.superuser,
                                               quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))

    def test_get_queryset_team_by_querying_scope_with_team_default_role(self):
        """
        Test that we can consume Team quota if permission is given in a Team's default role
        """
        # No instances
        self._assert_cannot_consume_quota(self.superuser)
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_cannot_consume_quota(self.user3)

        # Create a team organization
        org1 = Organization.objects.create(name="Organization #1")
        team1 = Team.objects.create(name="Team #1", org=org1)
        self.assertTrue(team1 in Team.objects.all())
        self.assertEqual(Team.objects.count(), 1)

        # Create Permission/Role
        role = Role.objects.create(name="View Team")
        role.permissions.add(self.permission_object)

        # Add role to team1
        team1.roles.add(role)

        # No user in org1 so only superuser can see
        self._assert_can_consume_only_quota_qs(self.superuser,
                                               quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_cannot_consume_quota(self.user3)

        # assign an empty role to user1 and user2
        org1.add_user_in_role(self.user1, self.empty_role)
        team1.add_user_in_role(self.user1, self.empty_role)
        org1.add_user_in_role(self.user2, self.empty_role)
        team1.add_user_in_role(self.user2, self.empty_role)

        # everyone can see except user3
        self._assert_can_consume_only_quota_qs(self.superuser,
                                               quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))
        self._assert_can_consume_only_quota_qs(self.user1, quota_qs=Scope.objects.filter(id__in=[team1.id]))
        self._assert_can_consume_only_quota_qs(self.user2, quota_qs=Scope.objects.filter(id__in=[team1.id]))
        self._assert_cannot_consume_quota(self.user3)

        # remove user2 from org
        org1.remove_user_in_role(self.user2, self.empty_role)

        # user1 is still in organization
        self._assert_can_consume_only_quota_qs(self.superuser,
                                               quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))
        self._assert_can_consume_only_quota_qs(self.user1, quota_qs=Scope.objects.filter(id__in=[team1.id]))
        self._assert_cannot_consume_quota(self.user2)
        self._assert_cannot_consume_quota(self.user3)

        # Remove view org to all organization's user
        team1.roles.remove(role)

        # only super can see
        self._assert_can_consume_only_quota_qs(self.superuser,
                                               quota_qs=Scope.objects.filter(id__in=[org1.id, team1.id]))
        self._assert_cannot_consume_quota(self.user1)
        self._assert_cannot_consume_quota(self.user2)
        self._assert_cannot_consume_quota(self.user3)
