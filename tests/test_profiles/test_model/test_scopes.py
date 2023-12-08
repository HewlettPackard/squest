from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from profiles.models import Team, Organization, AbstractScope, Scope, GlobalScope, Role

from tests.utils import TransactionTestUtils


class TestModelScope(TransactionTestUtils):

    def setUp(self):
        self.role1 = Role.objects.create(name="role1")
        self.role2 = Role.objects.create(name="role2")
        self.user1 = User.objects.create_user('user1', 'user1@hpe.com', "password")
        self.user2 = User.objects.create_user('user2', 'user2@hpe.com', "password")
        super(TestModelScope, self).setUp()

    def manage_user_in_scope_check(self, scope):
        # No users/rbac in org1
        self.assertEqual(scope.users.count(), 0)
        self.assertEqual(scope.rbac.count(), 0)

        # Assign role1 to user1 in scope
        scope.add_user_in_role(self.user1, self.role1)

        # One user in scope
        self.assertEqual(scope.users.count(), 1)
        self.assertEqual(scope.users.first(), self.user1)
        # One rbac in scope
        self.assertEqual(scope.rbac.count(), 1)

        # Assign role2 to user1 in scope
        scope.add_user_in_role(self.user1, self.role2)

        # Still one user in scope
        self.assertEqual(scope.users.count(), 1)
        # Org1 has two rbac
        self.assertEqual(scope.rbac.count(), 2)

        # Assign role1 to user2 in scope
        scope.add_user_in_role(self.user2, self.role1)

        # Two users in scope
        self.assertEqual(scope.users.count(), 2)
        # Still two RBAC
        self.assertEqual(scope.rbac.count(), 2)

        # Unassign role1 to user2 in scope
        scope.remove_user_in_role(self.user2, self.role1)

        # One user after remove
        self.assertEqual(scope.users.count(), 1)
        # Still 2 RBAC
        self.assertEqual(scope.rbac.count(), 2)

        # Unassign role1 and role2 to user1 in scope
        scope.remove_user(self.user1)

        # No users
        self.assertEqual(scope.users.count(), 0)
        # Still 2 RBAC
        self.assertEqual(scope.rbac.count(), 2)

    def test_can_create_org_and_teams(self):
        org_count = Organization.objects.count()
        team_count = Team.objects.count()

        # New org
        org1 = Organization.objects.create(name="Organization #1")

        # Org created
        self.assertEqual(org_count + 1, Organization.objects.count())

        # No team in org1
        self.assertEqual(0, org1.teams.count())

        # New team
        team1 = Team.objects.create(name="Team #1", org=org1)

        # Team created
        self.assertEqual(team_count + 1, Team.objects.count())

        # One team in org1
        self.assertEqual(1, org1.teams.count())
        self.assertEqual(team1, org1.teams.first())

    def test_get_object(self):
        org1 = Organization.objects.create(name="Organization #1")
        team1 = Team.objects.create(name="Team #1", org=org1)
        squest_scope = GlobalScope.load()

        # AbstractScope
        self.assertEqual(AbstractScope.objects.get(id=org1.id).get_object(), org1)
        self.assertEqual(AbstractScope.objects.get(id=team1.id).get_object(), team1)
        self.assertEqual(AbstractScope.objects.get(id=squest_scope.id).get_object(), squest_scope)

        # Scope
        self.assertEqual(Scope.objects.get(id=org1.id).get_object(), org1)
        self.assertEqual(Scope.objects.get(id=team1.id).get_object(), team1)

        # self
        self.assertEqual(org1.get_object(), org1)
        self.assertEqual(team1.get_object(), team1)
        self.assertEqual(squest_scope.get_object(), squest_scope)

    def test_get_scopes(self):
        org1 = Organization.objects.create(name="Organization #1")
        team1 = Team.objects.create(name="Team #1", org=org1)
        squest_scope = GlobalScope.load()

        self.assertListEqual(
            list(
                AbstractScope.objects.filter(id__in=[org1.id, team1.id, squest_scope.id]).values_list("id", flat=True)),
            list(team1.get_scopes().values_list("id", flat=True))
        )

        self.assertListEqual(
            list(AbstractScope.objects.filter(id__in=[org1.id, squest_scope.id]).values_list("id", flat=True)),
            list(org1.get_scopes().values_list("id", flat=True))
        )
        self.assertListEqual(
            list(AbstractScope.objects.filter(id__in=[squest_scope.id]).values_list("id", flat=True)),
            list(squest_scope.get_scopes().values_list("id", flat=True))
        )

    def test_manage_user_in_global_scope(self):
        global_scope = GlobalScope.load()
        self.manage_user_in_scope_check(global_scope)

    def test_manage_user_in_org(self):
        org1 = Organization.objects.create(name="Organization #1")
        self.manage_user_in_scope_check(org1)

    def test_manage_user_in_team(self):
        org1 = Organization.objects.create(name="Organization #1")
        org1.add_user_in_role(self.user1, self.role1)
        org1.add_user_in_role(self.user2, self.role1)
        team1 = Team.objects.create(name="Team #1", org=org1)
        self.manage_user_in_scope_check(team1)

    def test_remove_user_in_role_from_org_also_remove_user_in_teams(self):
        org1 = Organization.objects.create(name="Organization #1")
        org1.add_user_in_role(self.user1, self.role1)
        org1.add_user_in_role(self.user1, self.role2)
        team1 = Team.objects.create(name="Team #1", org=org1)
        team1.add_user_in_role(self.user1, self.role1)
        org1.remove_user_in_role(self.user1, self.role1)

        # Check that user1 still have role1 in team1 after remove role1 in org1
        self.assertTrue(team1.rbac.filter(role=self.role1, user=self.user1).exists())

        org1.remove_user_in_role(self.user1, self.role2)

        self.assertFalse(team1.users.exists())

    def test_remove_user_from_org_also_remove_user_in_teams(self):
        org1 = Organization.objects.create(name="Organization #1")
        org1.add_user_in_role(self.user1, self.role1)
        org1.add_user_in_role(self.user1, self.role2)
        team1 = Team.objects.create(name="Team #1", org=org1)
        team1.add_user_in_role(self.user1, self.role1)
        org1.remove_user(self.user1)
        self.assertFalse(team1.users.exists())

    def test_cannot_add_user_in_team_if_not_in_org(self):
        org1 = Organization.objects.create(name="Organization #1")
        team1 = Team.objects.create(name="Team #1", org=org1)
        with self.assertRaises(ValidationError):
            team1.add_user_in_role(self.user1, self.role1)

    def test_expand(self):
        # Empty queryset
        self.assertQuerysetEqualID(Scope.objects.none().expand(), Scope.objects.none())
        self.assertQuerysetEqualID(Scope.objects.all().expand(), Scope.objects.all())

        org1 = Organization.objects.create(name="Organization #1")
        teams = []
        teams.append(Team.objects.create(name="Team #1", org=org1))
        teams.append(Team.objects.create(name="Team #2", org=org1))
        teams.append(Team.objects.create(name="Team #3", org=org1))
        teams.append(Team.objects.create(name="Team #4", org=org1))

        queryset_test = Scope.objects.filter(id=org1.id)
        all_scopes = Scope.objects.none()
        all_scopes = all_scopes | Scope.objects.filter(id=org1.id)
        for team in teams:
            all_scopes |= Scope.objects.filter(id=team.id)

        self.assertQuerysetEqualID(queryset_test.expand(), all_scopes)
