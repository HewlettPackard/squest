from django.contrib.auth.models import User, Permission
from django.core.exceptions import ValidationError

from profiles.models import Team, Organization, AbstractScope, Scope, GlobalPermission, Role
from django.test.testcases import TransactionTestCase


class TestModelScopeGetQueryset(TransactionTestCase):

    def setUp(self):
        self.role1 = Role.objects.first()
        self.role2 = Role.objects.exclude(id=self.role1.id).first()
        self.user1 = User.objects.create_user('user1', 'user1@hpe.com', "password")
        self.user2 = User.objects.create_user('user2', 'user2@hpe.com', "password")
        super(TestModelScopeGetQueryset, self).setUp()

    def test_get_queryset_global_permission_with_global_permission_role(self):
        role = Role.objects.create(name="View global permission")
        permission = "profiles.view_globalpermission"
        app_label, codename = permission.split('.')
        role.permissions.add(
            Permission.objects.get(content_type__app_label=app_label, content_type__model="globalpermission",
                                   codename=codename))
        self.assertEqual(GlobalPermission.get_queryset_for_user(self.user1, permission).count(), 0)
        global_perm = GlobalPermission.load()
        global_perm.add_user_in_role(self.user1, role)
        self.assertEqual(GlobalPermission.get_queryset_for_user(self.user1, permission).count(), 1)

    def test_get_queryset_organization_with_global_permission_role(self):
        role = Role.objects.create(name="View organization")
        permission = "profiles.view_organization"
        app_label, codename = permission.split('.')
        role.permissions.add(
            Permission.objects.get(content_type__app_label=app_label, content_type__model="organization",
                                   codename=codename))
        self.assertEqual(Organization.get_queryset_for_user(self.user1, permission).count(), 0)

        global_perm = GlobalPermission.load()
        global_perm.add_user_in_role(self.user1, role)

        initital_org_count = Organization.get_queryset_for_user(self.user1, permission).count()

        Organization.objects.create(name="Organization #1")
        self.assertEqual(Organization.get_queryset_for_user(self.user1, permission).count(), initital_org_count + 1)
        Organization.objects.create(name="Organization #2")
        self.assertEqual(Organization.get_queryset_for_user(self.user1, permission).count(), initital_org_count + 2)
        Organization.objects.create(name="Organization #3")
        self.assertEqual(Organization.get_queryset_for_user(self.user1, permission).count(), initital_org_count + 3)

    def test_get_queryset_organization_with_organization_role(self):
        role = Role.objects.create(name="View organization")
        permission = "profiles.view_organization"
        app_label, codename = permission.split('.')
        role.permissions.add(
            Permission.objects.get(content_type__app_label=app_label, content_type__model="organization",
                                   codename=codename))

        org1 = Organization.objects.create(name="Organization #1")
        org2 = Organization.objects.create(name="Organization #2")
        org3 = Organization.objects.create(name="Organization #3")

        self.assertEqual(Organization.get_queryset_for_user(self.user1, permission).count(), 0)

        org1.add_user_in_role(self.user1, role)
        self.assertEqual(Organization.get_queryset_for_user(self.user1, permission).count(), 1)

        org2.add_user_in_role(self.user1, role)
        self.assertEqual(Organization.get_queryset_for_user(self.user1, permission).count(), 2)

        org3.add_user_in_role(self.user1, role)
        self.assertEqual(Organization.get_queryset_for_user(self.user1, permission).count(), 3)

    def test_get_queryset_team_with_global_permission_role(self):
        role = Role.objects.create(name="View team")
        permission = "profiles.view_team"
        app_label, codename = permission.split('.')
        role.permissions.add(
            Permission.objects.get(content_type__app_label=app_label, content_type__model="team",
                                   codename=codename))
        org1 = Organization.objects.create(name="Organization #1")
        org2 = Organization.objects.create(name="Organization #2")
        team1 = Team.objects.create(name="Team #1", org=org1)
        team2 = Team.objects.create(name="Team #2", org=org1)
        team3 = Team.objects.create(name="Team #3", org=org2)

        self.assertEqual(Team.get_queryset_for_user(self.user1, permission).count(), 0)

        global_perm = GlobalPermission.load()
        global_perm.add_user_in_role(self.user1, role)

        self.assertEqual(Team.get_queryset_for_user(self.user1, permission).count(), 3)

    def test_get_queryset_team_with_organization_role(self):
        role = Role.objects.create(name="View team")
        permission = "profiles.view_team"
        app_label, codename = permission.split('.')
        role.permissions.add(
            Permission.objects.get(content_type__app_label=app_label, content_type__model="team",
                                   codename=codename))

        org1 = Organization.objects.create(name="Organization #1")
        org2 = Organization.objects.create(name="Organization #2")
        team1 = Team.objects.create(name="Team #1", org=org1)
        team2 = Team.objects.create(name="Team #2", org=org1)
        team3 = Team.objects.create(name="Team #3", org=org2)

        self.assertEqual(Team.get_queryset_for_user(self.user1, permission).count(), 0)

        org1.add_user_in_role(self.user1, role)
        self.assertEqual(Team.get_queryset_for_user(self.user1, permission).count(), 2)

        org2.add_user_in_role(self.user1, role)
        self.assertEqual(Team.get_queryset_for_user(self.user1, permission).count(), 3)

    def test_get_queryset_team_with_team_role(self):
        role = Role.objects.create(name="View team")
        empty_role = Role.objects.create(name="Empty")
        permission = "profiles.view_team"
        app_label, codename = permission.split('.')
        role.permissions.add(
            Permission.objects.get(content_type__app_label=app_label, content_type__model="team",
                                   codename=codename))

        org1 = Organization.objects.create(name="Organization #1")
        org2 = Organization.objects.create(name="Organization #2")
        org1.add_user_in_role(self.user1, empty_role)
        org2.add_user_in_role(self.user1, empty_role)
        org1_team1 = Team.objects.create(name="Team #1", org=org1)
        org1_team2 = Team.objects.create(name="Team #2", org=org1)
        org2_team1 = Team.objects.create(name="Team #3", org=org2)

        self.assertEqual(Team.get_queryset_for_user(self.user1, permission).count(), 0)

        org1_team1.add_user_in_role(self.user1, role)
        self.assertEqual(Team.get_queryset_for_user(self.user1, permission).count(), 1)

        org1_team2.add_user_in_role(self.user1, role)
        self.assertEqual(Team.get_queryset_for_user(self.user1, permission).count(), 2)

        org2_team1.add_user_in_role(self.user1, role)
        self.assertEqual(Team.get_queryset_for_user(self.user1, permission).count(), 3)
