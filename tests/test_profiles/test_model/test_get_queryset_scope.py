from django.contrib.auth.models import User

from profiles.models import Team, Organization, GlobalPermission, Role
from profiles.models.squest_permission import Permission

from tests.utils import TransactionTestUtils


class TestModelScopeGetQueryset(TransactionTestUtils):

    def setUp(self):
        super(TestModelScopeGetQueryset, self).setUp()
        self.user1 = User.objects.create_user('user1', 'user1@hpe.com', "password")
        self.user2 = User.objects.create_user('user2', 'user2@hpe.com', "password")
        self.user3 = User.objects.create_user('user3', 'user3@hpe.com', "password")
        self.superuser = User.objects.create_superuser("superuser")

        self.global_perm = GlobalPermission.load()
        self.empty_role = Role.objects.create(name="Empty role")

    def _assert_can_see_everything(self, cls, user):
        self.assertQuerysetEqualID(
            cls.get_queryset_for_user(user, f"{cls._meta.app_label}.view_{cls._meta.model_name}"),
            cls.objects.all())

    def _assert_can_see_nothing(self, cls, user):
        self.assertQuerysetEqualID(
            cls.get_queryset_for_user(user, f"{cls._meta.app_label}.view_{cls._meta.model_name}"),
            cls.objects.none())

    def test_get_queryset_global_permission_with_global_permission_role(self):
        """
        Test that we can see GlobalPermission if permission is given in a GlobalPermission's role
        """

        # Only superuser can see
        self._assert_can_see_nothing(GlobalPermission, self.user1)
        self._assert_can_see_nothing(GlobalPermission, self.user2)
        self._assert_can_see_everything(GlobalPermission, self.superuser)

        # Create role to view GlobalPermission
        role = Role.objects.create(name="View global permission")
        permission_object = Permission.objects.get(content_type__app_label="profiles",
                                                   content_type__model="globalpermission",
                                                   codename="view_globalpermission")
        role.permissions.add(permission_object)

        # Assigne role to view GlobalPermission to user1
        self.global_perm.add_user_in_role(self.user1, role)

        # Only superuser and user1 can see it
        self._assert_can_see_everything(GlobalPermission, self.user1)
        self._assert_can_see_nothing(GlobalPermission, self.user2)
        self._assert_can_see_everything(GlobalPermission, self.superuser)

        # remove role to view GlobalPermission to user1
        self.global_perm.remove_user_in_role(self.user1, role)

        # Only superuser can see
        self._assert_can_see_nothing(GlobalPermission, self.user1)
        self._assert_can_see_nothing(GlobalPermission, self.user2)
        self._assert_can_see_everything(GlobalPermission, self.superuser)

    def test_get_queryset_global_permission_with_global_default_permissions(self):
        """
        Test that we can see GlobalPermission if permission is given in a GlobalPermission's permission
        """

        # Only superuser can see
        self._assert_can_see_nothing(GlobalPermission, self.user1)
        self._assert_can_see_nothing(GlobalPermission, self.user2)
        self._assert_can_see_everything(GlobalPermission, self.superuser)

        # Create permission to view GlobalPermission
        permission_object = Permission.objects.get(content_type__app_label="profiles",
                                                   content_type__model="globalpermission",
                                                   codename="view_globalpermission")

        # Assign permission to all squest user without exception
        self.global_perm.default_permissions.add(permission_object)

        # Everyone can see it
        self._assert_can_see_everything(GlobalPermission, self.user1)
        self._assert_can_see_everything(GlobalPermission, self.user2)
        self._assert_can_see_everything(GlobalPermission, self.superuser)

        # Remove permission to all squest user without exception
        self.global_perm.default_permissions.remove(permission_object)

        # Only superuser can see
        self._assert_can_see_nothing(GlobalPermission, self.user1)
        self._assert_can_see_nothing(GlobalPermission, self.user2)
        self._assert_can_see_everything(GlobalPermission, self.superuser)

    def test_get_queryset_organization_with_global_permission_role(self):
        """
        Test that we can see Organization if permission is given in a GlobalPermission's role
        """

        # Only superuser can see
        self._assert_can_see_nothing(Organization, self.user1)
        self._assert_can_see_nothing(Organization, self.user2)
        self._assert_can_see_everything(Organization, self.superuser)

        # Create role to view Organization
        role = Role.objects.create(name="View Organization")
        permission_object = Permission.objects.get(content_type__app_label="profiles",
                                                   content_type__model="organization",
                                                   codename="view_organization")
        role.permissions.add(permission_object)

        # Assign role to view Organization to user1
        self.global_perm.add_user_in_role(self.user1, role)

        # Create a new organization
        org1 = Organization.objects.create(name="Organization #1")
        self.assertTrue(org1 in Organization.objects.all())
        self.assertEqual(Organization.objects.count(), 1)

        # Only user1 can see it
        self._assert_can_see_everything(Organization, self.user1)
        self._assert_can_see_nothing(Organization, self.user2)
        self._assert_can_see_everything(Organization, self.superuser)

        # Remove permission to user1
        self.global_perm.remove_user_in_role(self.user1, role)

        # Only superuser can see
        self._assert_can_see_nothing(Organization, self.user1)
        self._assert_can_see_nothing(Organization, self.user2)
        self._assert_can_see_everything(Organization, self.superuser)

    def test_get_queryset_organization_with_global_permission__default_permissions(self):
        """
        Test that we can see Organization if permission is given in a GlobalPermission's perm
        """

        # Only superuser can see
        self._assert_can_see_nothing(Organization, self.user1)
        self._assert_can_see_nothing(Organization, self.user2)
        self._assert_can_see_everything(Organization, self.superuser)

        # Create Permission/Role
        permission_object = Permission.objects.get(content_type__app_label="profiles",
                                                   content_type__model="organization",
                                                   codename="view_organization")

        # Assign permission to all users
        self.global_perm.default_permissions.add(permission_object)

        # Create a new organization
        org1 = Organization.objects.create(name="Organization #1")
        self.assertTrue(org1 in Organization.objects.all())
        self.assertEqual(Organization.objects.count(), 1)

        # Everyone can see it
        self._assert_can_see_everything(Organization, self.user1)
        self._assert_can_see_everything(Organization, self.user2)
        self._assert_can_see_everything(Organization, self.superuser)

        # Remove permission to all users
        self.global_perm.default_permissions.remove(permission_object)

        # Only superuser can see
        self._assert_can_see_nothing(Organization, self.user1)
        self._assert_can_see_nothing(Organization, self.user2)
        self._assert_can_see_everything(Organization, self.superuser)

    def test_get_queryset_team_with_global_permission_role(self):
        """
        Test that we can see Team if permission is given in a GlobalPermission's role
        """
        # Only superuser can see
        self._assert_can_see_nothing(Team, self.user1)
        self._assert_can_see_nothing(Team, self.user2)
        self._assert_can_see_everything(Team, self.superuser)

        # Create Permission/Role
        role = Role.objects.create(name="View Team")
        permission_object = Permission.objects.get(content_type__app_label="profiles",
                                                   content_type__model="team",
                                                   codename="view_team")
        role.permissions.add(permission_object)

        # Assign role to user1
        self.global_perm.add_user_in_role(self.user1, role)

        # Create a new organization/team
        org1 = Organization.objects.create(name="Organization #1")
        team1 = Team.objects.create(name="Team #1", org=org1)
        self.assertTrue(team1 in Team.objects.all())
        self.assertEqual(Team.objects.count(), 1)

        # user1 can see it
        self._assert_can_see_everything(Team, self.user1)
        self._assert_can_see_nothing(Team, self.user2)
        self._assert_can_see_everything(Team, self.superuser)

        # Remove role to user1
        self.global_perm.remove_user_in_role(self.user1, role)

        # Only superuser can see
        self._assert_can_see_nothing(Team, self.user1)
        self._assert_can_see_nothing(Team, self.user2)
        self._assert_can_see_everything(Team, self.superuser)

    def test_get_queryset_team_with_global_permission__default_permissions(self):
        """
        Test that we can see Team if permission is given in a GlobalPermission's perm
        """
        # Only superuser can see
        self._assert_can_see_nothing(Team, self.user1)
        self._assert_can_see_nothing(Team, self.user2)
        self._assert_can_see_everything(Team, self.superuser)

        # Create Permission/Role
        permission_object = Permission.objects.get(content_type__app_label="profiles",
                                                   content_type__model="team",
                                                   codename="view_team")
        self.global_perm.default_permissions.add(permission_object)

        # Create a new organization/team
        org1 = Organization.objects.create(name="Organization #1")
        team1 = Team.objects.create(name="Team #1", org=org1)
        self.assertTrue(team1 in Team.objects.all())
        self.assertEqual(Team.objects.count(), 1)

        # Everyone can see it
        self._assert_can_see_everything(Team, self.user1)
        self._assert_can_see_everything(Team, self.user2)
        self._assert_can_see_everything(Team, self.superuser)

        # Remove role to everyone
        self.global_perm.default_permissions.remove(permission_object)

        # Only superuser can see
        self._assert_can_see_nothing(Team, self.user1)
        self._assert_can_see_nothing(Team, self.user2)
        self._assert_can_see_everything(Team, self.superuser)

    def test_get_queryset_organization_with_organization_role(self):
        """
        Test that we can see Organization if permission is given in an Organization's role
        """

        # Only superuser can see
        self._assert_can_see_nothing(Organization, self.user1)
        self._assert_can_see_nothing(Organization, self.user2)
        self._assert_can_see_everything(Organization, self.superuser)

        # Create Permission/Role
        role = Role.objects.create(name="View Organization")
        permission_object = Permission.objects.get(content_type__app_label="profiles",
                                                   content_type__model="organization",
                                                   codename="view_organization")
        role.permissions.add(permission_object)

        # Create a new organization
        org1 = Organization.objects.create(name="Organization #1")
        self.assertTrue(org1 in Organization.objects.all())
        self.assertEqual(Organization.objects.count(), 1)

        # Only superuser can see it
        self._assert_can_see_nothing(Organization, self.user1)
        self._assert_can_see_nothing(Organization, self.user2)
        self._assert_can_see_everything(Organization, self.superuser)

        # Assign role to user1
        org1.add_user_in_role(self.user1, role)

        # user1 can see it
        self._assert_can_see_everything(Organization, self.user1)
        self._assert_can_see_nothing(Organization, self.user2)
        self._assert_can_see_everything(Organization, self.superuser)

        # Remove role to user1
        org1.remove_user_in_role(self.user1, role)

        # Only superuser can see
        self._assert_can_see_nothing(Organization, self.user1)
        self._assert_can_see_nothing(Organization, self.user2)
        self._assert_can_see_everything(Organization, self.superuser)

    def test_get_queryset_organization_with_organization_default_role(self):
        """
        Test that we can see Organization if permission is given in a Organization's default role
        """

        # Only superuser can see it
        self._assert_can_see_everything(Organization, self.superuser)
        self._assert_can_see_nothing(Organization, self.user1)
        self._assert_can_see_nothing(Organization, self.user2)
        self._assert_can_see_nothing(Organization, self.user3)

        # Create a new organization
        org1 = Organization.objects.create(name="Organization #1")
        self.assertTrue(org1 in Organization.objects.all())
        self.assertEqual(Organization.objects.count(), 1)

        # Create Permission/Role
        role = Role.objects.create(name="View Organization")
        permission_object = Permission.objects.get(content_type__app_label="profiles",
                                                   content_type__model="organization",
                                                   codename="view_organization")
        role.permissions.add(permission_object)

        # Add view org to all organization's user
        org1.roles.add(role)

        # No user in org1 so only superuser can see
        self._assert_can_see_everything(Organization, self.superuser)
        self._assert_can_see_nothing(Organization, self.user1)
        self._assert_can_see_nothing(Organization, self.user2)
        self._assert_can_see_nothing(Organization, self.user3)

        # assign an empty role to user1 and user2
        org1.add_user_in_role(self.user1, self.empty_role)
        org1.add_user_in_role(self.user2, self.empty_role)

        # everyone can see except user3
        self._assert_can_see_everything(Organization, self.superuser)
        self._assert_can_see_everything(Organization, self.user1)
        self._assert_can_see_everything(Organization, self.user2)
        self._assert_can_see_nothing(Organization, self.user3)

        # remove user2 from org
        org1.remove_user_in_role(self.user2, self.empty_role)

        # user1 is still in organization
        self._assert_can_see_everything(Organization, self.superuser)
        self._assert_can_see_everything(Organization, self.user1)
        self._assert_can_see_nothing(Organization, self.user2)
        self._assert_can_see_nothing(Organization, self.user3)

        # Remove view org to all organization's user
        org1.roles.remove(role)

        # only super can see
        self._assert_can_see_everything(Organization, self.superuser)
        self._assert_can_see_nothing(Organization, self.user1)
        self._assert_can_see_nothing(Organization, self.user2)
        self._assert_can_see_nothing(Organization, self.user3)

    def test_get_queryset_team_with_organization_role(self):
        """
        Test that we can see Team if permission is given in a Organization's role
        """

        # Only superuser can see
        self._assert_can_see_nothing(Team, self.user1)
        self._assert_can_see_nothing(Team, self.user2)
        self._assert_can_see_everything(Team, self.superuser)

        # Create Permission/Role
        role = Role.objects.create(name="View Team")
        permission_object = Permission.objects.get(content_type__app_label="profiles",
                                                   content_type__model="team",
                                                   codename="view_team")
        role.permissions.add(permission_object)

        # Create a new organization
        org1 = Organization.objects.create(name="Organization #1")
        team1 = Team.objects.create(name="Team #1", org=org1)
        self.assertTrue(team1 in Team.objects.all())
        self.assertEqual(Team.objects.count(), 1)

        # Only superuser can see
        self._assert_can_see_nothing(Team, self.user1)
        self._assert_can_see_nothing(Team, self.user2)
        self._assert_can_see_everything(Team, self.superuser)

        # Assign role to user1
        org1.add_user_in_role(self.user1, role)

        # user1 can see it
        self._assert_can_see_everything(Team, self.user1)
        self._assert_can_see_nothing(Team, self.user2)
        self._assert_can_see_everything(Team, self.superuser)

        # Remove role to user1
        org1.remove_user_in_role(self.user1, role)

        # Only superuser can see
        self._assert_can_see_nothing(Team, self.user1)
        self._assert_can_see_nothing(Team, self.user2)
        self._assert_can_see_everything(Team, self.superuser)

    def test_get_queryset_team_with_organization_default_role(self):
        """
        Test that we can see Team if permission is given in a Organization's default role
        """
        # No instances
        self._assert_can_see_nothing(Team, self.superuser)
        self._assert_can_see_nothing(Team, self.user1)
        self._assert_can_see_nothing(Team, self.user2)
        self._assert_can_see_nothing(Team, self.user3)

        # Create a team/organization
        org1 = Organization.objects.create(name="Organization #1")
        team1 = Team.objects.create(name="Team #1", org=org1)
        self.assertTrue(team1 in Team.objects.all())
        self.assertEqual(Team.objects.count(), 1)

        # Add view org to all organization's user
        role = Role.objects.create(name="View Team")
        permission_object = Permission.objects.get(content_type__app_label="profiles",
                                                   content_type__model="team",
                                                   codename="view_team")
        role.permissions.add(permission_object)

        # Assign role to the whole organization
        org1.roles.add(role)

        # No user in org1 so only superuser can see
        self._assert_can_see_everything(Team, self.superuser)
        self._assert_can_see_nothing(Team, self.user1)
        self._assert_can_see_nothing(Team, self.user2)
        self._assert_can_see_nothing(Team, self.user3)

        # assign an empty role to user1 and user2
        org1.add_user_in_role(self.user1, self.empty_role)
        org1.add_user_in_role(self.user2, self.empty_role)

        # everyone can see except user3
        self._assert_can_see_everything(Team, self.superuser)
        self._assert_can_see_everything(Team, self.user1)
        self._assert_can_see_everything(Team, self.user2)
        self._assert_can_see_nothing(Team, self.user3)

        # remove user2 from org
        org1.remove_user_in_role(self.user2, self.empty_role)

        # user1 is still in organization
        self._assert_can_see_everything(Team, self.superuser)
        self._assert_can_see_everything(Team, self.user1)
        self._assert_can_see_nothing(Team, self.user2)
        self._assert_can_see_nothing(Team, self.user3)

        # Remove view org to all organization's user
        org1.roles.remove(role)

        # only super can see
        self._assert_can_see_everything(Team, self.superuser)
        self._assert_can_see_nothing(Team, self.user1)
        self._assert_can_see_nothing(Team, self.user2)
        self._assert_can_see_nothing(Team, self.user3)

    def test_get_queryset_team_with_team_role(self):
        """
        Test that we can see Team if permission is given in a Team's role
        """

        # Only superuser can see
        self._assert_can_see_nothing(Team, self.user1)
        self._assert_can_see_nothing(Team, self.user2)
        self._assert_can_see_everything(Team, self.superuser)

        # Create Permission/Role
        role = Role.objects.create(name="View Team")
        permission_object = Permission.objects.get(content_type__app_label="profiles",
                                                   content_type__model="team",
                                                   codename="view_team")
        role.permissions.add(permission_object)

        # Create a new organization
        org1 = Organization.objects.create(name="Organization #1")
        team1 = Team.objects.create(name="Team #1", org=org1)
        self.assertTrue(team1 in Team.objects.all())
        self.assertEqual(Team.objects.count(), 1)

        self._assert_can_see_nothing(Team, self.user1)
        self._assert_can_see_nothing(Team, self.user2)
        self._assert_can_see_everything(Team, self.superuser)

        # Assign role to user1
        org1.add_user_in_role(self.user1, self.empty_role)
        team1.add_user_in_role(self.user1, role)

        # user1 can see it
        self._assert_can_see_everything(Team, self.user1)
        self._assert_can_see_nothing(Team, self.user2)
        self._assert_can_see_everything(Team, self.superuser)

        # Remove role to user1
        team1.remove_user_in_role(self.user1, role)

        # Only superuser can see it
        self._assert_can_see_nothing(Team, self.user1)
        self._assert_can_see_nothing(Team, self.user2)
        self._assert_can_see_everything(Team, self.superuser)

    def test_get_queryset_team_with_team_default_role(self):
        """
        Test that we can see Team if permission is given in a Team's default role
        """
        # No instances
        self._assert_can_see_nothing(Team, self.superuser)
        self._assert_can_see_nothing(Team, self.user1)
        self._assert_can_see_nothing(Team, self.user2)
        self._assert_can_see_nothing(Team, self.user3)

        # Create a team organization
        org1 = Organization.objects.create(name="Organization #1")
        team1 = Team.objects.create(name="Team #1", org=org1)
        self.assertTrue(team1 in Team.objects.all())
        self.assertEqual(Team.objects.count(), 1)

        # Create Permission/Role
        role = Role.objects.create(name="View Team")
        permission_object = Permission.objects.get(content_type__app_label="profiles",
                                                   content_type__model="team",
                                                   codename="view_team")
        role.permissions.add(permission_object)

        # Add role to team1
        team1.roles.add(role)

        # No user in org1 so only superuser can see
        self._assert_can_see_everything(Team, self.superuser)
        self._assert_can_see_nothing(Team, self.user1)
        self._assert_can_see_nothing(Team, self.user2)
        self._assert_can_see_nothing(Team, self.user3)

        # assign an empty role to user1 and user2
        org1.add_user_in_role(self.user1, self.empty_role)
        team1.add_user_in_role(self.user1, self.empty_role)
        org1.add_user_in_role(self.user2, self.empty_role)
        team1.add_user_in_role(self.user2, self.empty_role)

        # everyone can see except user3
        self._assert_can_see_everything(Team, self.superuser)
        self._assert_can_see_everything(Team, self.user1)
        self._assert_can_see_everything(Team, self.user2)
        self._assert_can_see_nothing(Team, self.user3)

        # remove user2 from org
        org1.remove_user_in_role(self.user2, self.empty_role)

        # user1 is still in organization
        self._assert_can_see_everything(Team, self.superuser)
        self._assert_can_see_everything(Team, self.user1)
        self._assert_can_see_nothing(Team, self.user2)
        self._assert_can_see_nothing(Team, self.user3)

        # Remove view org to all organization's user
        team1.roles.remove(role)

        # only super can see
        self._assert_can_see_everything(Team, self.superuser)
        self._assert_can_see_nothing(Team, self.user1)
        self._assert_can_see_nothing(Team, self.user2)
        self._assert_can_see_nothing(Team, self.user3)
