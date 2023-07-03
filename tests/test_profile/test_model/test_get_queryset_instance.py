from django.contrib.auth.models import User, Permission

from profiles.models import Team, Organization, GlobalPermission, Role
from django.test.testcases import TransactionTestCase

from service_catalog.models import Instance


class TestModelScopeGetQuerysetInstance(TransactionTestCase):

    def assertQuerysetEqualID(self, qs1, qs2, value="id"):
        return self.assertListEqual(list(qs1.values_list(value, flat=True)), list(qs2.values_list(value, flat=True)))

    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'user1@hpe.com', "password")
        self.user2 = User.objects.create_user('user2', 'user2@hpe.com', "password")
        super(TestModelScopeGetQuerysetInstance, self).setUp()

        self.role_view_instance = Role.objects.create(name="View global instances")
        self.permission = "service_catalog.view_instance"
        app_label, codename = self.permission.split('.')
        self.role_view_instance.permissions.add(
            Permission.objects.get(content_type__app_label=app_label, content_type__model="instance",
                                   codename=codename))
        self.global_perm = GlobalPermission.load()

    def test_get_queryset_instance_with_global_permission_role(self):
        org1 = Organization.objects.create(name="Organization #1")

        # Add instance1 in org1
        instance1 = Instance.objects.create(name="Instance #1")
        instance1.scopes.add(org1)

        # user1 and user2 can't see any instances (no role for them)
        self.assertEqual(Instance.get_queryset_for_user(self.user1, self.permission).count(), 0)
        self.assertEqual(Instance.get_queryset_for_user(self.user2, self.permission).count(), 0)

        # Assign view_instance to user1 in GlobalPerm
        self.global_perm.add_user_in_role(self.user1, self.role_view_instance)

        # user1 can see all instances and user2 can't see anything
        self.assertEqual(Instance.get_queryset_for_user(self.user1, self.permission).count(), 1)
        self.assertQuerysetEqualID(
            Instance.get_queryset_for_user(self.user1, self.permission),
            Instance.objects.all()
        )
        self.assertEqual(Instance.get_queryset_for_user(self.user2, self.permission).count(), 0)

        # instance2 in team1
        team1org1 = Team.objects.create(name="Team #1", org=org1)
        instance2team1org1 = Instance.objects.create(name="Instance #2")
        instance2team1org1.scopes.add(team1org1)

        # user1 can see two instances and user2 can't see anything
        self.assertEqual(Instance.get_queryset_for_user(self.user1, self.permission).count(), 2)
        self.assertQuerysetEqualID(
            Instance.get_queryset_for_user(self.user1, self.permission),
            Instance.objects.all()
        )
        self.assertEqual(Instance.get_queryset_for_user(self.user2, self.permission).count(), 0)

        # instance3 without scopes
        Instance.objects.create(name="Instance #3")

        # user1 can see three instances and user2 can't see anything
        self.assertEqual(Instance.get_queryset_for_user(self.user1, self.permission).count(), 3)
        self.assertQuerysetEqualID(
            Instance.get_queryset_for_user(self.user1, self.permission),
            Instance.objects.all()
        )
        self.assertEqual(Instance.get_queryset_for_user(self.user2, self.permission).count(), 0)

    def test_get_queryset_instance_with_organization_role(self):
        org1 = Organization.objects.create(name="Organization #1")

        # Add instance1 in org1
        instance1 = Instance.objects.create(name="Instance #1")
        instance1.scopes.add(org1)

        # user1 and user2 can't see any instances
        self.assertEqual(Instance.get_queryset_for_user(self.user1, self.permission).count(), 0)
        self.assertEqual(Instance.get_queryset_for_user(self.user2, self.permission).count(), 0)

        org1.add_user_in_role(self.user1, self.role_view_instance)

        # user1 can see it and user2 can't see anything
        self.assertEqual(Instance.get_queryset_for_user(self.user1, self.permission).count(), 1)
        self.assertQuerysetEqualID(
            Instance.get_queryset_for_user(self.user1, self.permission),
            org1.scope_instances.all()
        )
        self.assertEqual(Instance.get_queryset_for_user(self.user2, self.permission).count(), 0)

        # instance2 in team2
        team1 = Team.objects.create(name="Team #1", org=org1)
        instance2 = Instance.objects.create(name="Instance #2")
        instance2.scopes.add(team1)

        # user1 can see two instances and user2 can't see anything
        self.assertEqual(Instance.get_queryset_for_user(self.user1, self.permission).count(), 2)
        self.assertQuerysetEqualID(
            Instance.get_queryset_for_user(self.user1, self.permission),
            org1.scope_instances.all() | team1.scope_instances.all()
        )
        self.assertEqual(Instance.get_queryset_for_user(self.user2, self.permission).count(), 0)

        # instance3 in team 2 org 2
        org2 = Organization.objects.create(name="Organization #2")
        team2 = Team.objects.create(name="Team #2", org=org2)
        instance3 = Instance.objects.create(name="Instance #3")
        instance3.scopes.add(team2)

        # user1 can see two instances and user2 can't see anything (instance 3 isn't visible for them)
        self.assertEqual(Instance.get_queryset_for_user(self.user1, self.permission).count(), 2)
        self.assertQuerysetEqualID(
            Instance.get_queryset_for_user(self.user1, self.permission),
            org1.scope_instances.all() | team1.scope_instances.all()
        )
        self.assertEqual(Instance.get_queryset_for_user(self.user2, self.permission).count(), 0)

    def test_get_queryset_instance_with_team_role(self):
        org1 = Organization.objects.create(name="Organization #1")

        # Add instance1 in org1
        instance1 = Instance.objects.create(name="Instance #1")
        instance1.scopes.add(org1)

        # user1 and user2 can't see any instances
        self.assertEqual(Instance.get_queryset_for_user(self.user1, self.permission).count(), 0)
        self.assertEqual(Instance.get_queryset_for_user(self.user2, self.permission).count(), 0)

        # instance2 in team2
        team1 = Team.objects.create(name="Team #1", org=org1)
        instance2 = Instance.objects.create(name="Instance #2")
        instance2.scopes.add(team1)

        # Assign view instance to user1 in team1 only
        org1.add_user_in_role(self.user1, Role.objects.create(name="Empty role"))
        team1.add_user_in_role(self.user1, self.role_view_instance)

        # user1 can see instance2 only and user2 can't see anything
        self.assertEqual(Instance.get_queryset_for_user(self.user1, self.permission).count(), 1)
        self.assertQuerysetEqualID(
            Instance.get_queryset_for_user(self.user1, self.permission),
            team1.scope_instances.all()
        )
        self.assertEqual(Instance.get_queryset_for_user(self.user2, self.permission).count(), 0)

        # instance3 in team2 in org1
        team2 = Team.objects.create(name="Team #1", org=org1)
        instance3 = Instance.objects.create(name="Instance #3")
        instance3.scopes.add(team2)

        # user1 can see instance2 only and user2 can't see anything
        self.assertEqual(Instance.get_queryset_for_user(self.user1, self.permission).count(), 1)
        self.assertQuerysetEqualID(
            Instance.get_queryset_for_user(self.user1, self.permission),
            team1.scope_instances.all()
        )
        self.assertEqual(Instance.get_queryset_for_user(self.user2, self.permission).count(), 0)
