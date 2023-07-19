from django.contrib.auth.models import User, Permission

from profiles.models import Team, Organization, GlobalPermission, Role
from django.test.testcases import TransactionTestCase

from service_catalog.models import Instance, Support


class TestModelScopeGetQuerysetSupport(TransactionTestCase):

    def assertQuerysetEqualID(self, qs1, qs2):
        self.assertEqual(qs1.model, qs2.model)
        self.assertListEqual(list(qs1.values_list("id", flat=True)), list(qs2.values_list("id", flat=True)))

    def setUp(self):
        super(TestModelScopeGetQuerysetSupport, self).setUp()

        self.default_quota_scope = Organization.objects.create(name="Default scope for tests")

        self.user1 = User.objects.create_user('user1', 'user1@hpe.com', "password")
        self.user2 = User.objects.create_user('user2', 'user2@hpe.com', "password")
        self.user3 = User.objects.create_user('user3', 'user3@hpe.com', "password")
        self.superuser = User.objects.create_superuser("superuser")

        self.role_view_instance = Role.objects.create(name="View global instances")
        self.empty_role = Role.objects.create(name="Empty role")
        self.permission = "service_catalog.view_request"
        app_label, codename = self.permission.split('.')
        self.permission_object = Permission.objects.get(content_type__app_label=app_label,
                                                        content_type__model="request",
                                                        codename=codename)
        self.role_view_instance.permissions.add(self.permission_object)
        self.global_perm = GlobalPermission.load()

    def _assert_can_see_everything(self, user):
        self.assertQuerysetEqualID(Support.get_queryset_for_user(user, self.permission),
                                   Support.objects.all())

    def _assert_can_see_nothing(self, user):
        self.assertQuerysetEqualID(Support.get_queryset_for_user(user, self.permission),
                                   Support.objects.none())

    def test_get_queryset_globalpermission_user_permissions(self):
        """
        Test the user_permissions in global permission
        """

        # No instances
        self._assert_can_see_nothing(self.superuser)
        self._assert_can_see_nothing(self.user1)

        # create a new request
        instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
        request1 = Support.objects.create(instance=instance1)
        self.assertTrue(request1 in Support.objects.all())
        self.assertEqual(Support.objects.count(), 1)

        # add global perm
        self.global_perm.user_permissions.add(self.permission_object)

        # everyone can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_everything(self.user1)

        # remove global perm
        self.global_perm.user_permissions.remove(self.permission_object)

        # only super can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_nothing(self.user1)

    def test_get_queryset_globalpermission_perm_specific_user(self):
        """
        Test the rbac role in global permission
        """
        # No instances
        self._assert_can_see_nothing(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)

        # create a new request
        instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
        request1 = Support.objects.create(instance=instance1)
        self.assertTrue(request1 in Support.objects.all())
        self.assertEqual(Support.objects.count(), 1)

        # assign a view instance to user1
        self.global_perm.add_user_in_role(self.user1, self.role_view_instance)

        # everyone can see except user2
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_everything(self.user1)
        self._assert_can_see_nothing(self.user2)

        # unassign view instance role to user1
        self.global_perm.remove_user_in_role(self.user1, self.role_view_instance)

        # only super can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)

    def test_get_queryset_instance_with_organization_role(self):
        """
        Test the organization's role
        """
        # No instances
        self._assert_can_see_nothing(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)

        # create a new request
        instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
        request1 = Support.objects.create(instance=instance1)
        self.assertTrue(request1 in Support.objects.all())
        self.assertEqual(Support.objects.count(), 1)

        # Add org1 into instance1 scopes
        org1 = Organization.objects.create(name="Organization #1")
        instance1.scopes.add(org1)

        # assign a view instance to user1
        org1.add_user_in_role(self.user1, self.role_view_instance)

        # everyone can see except user2
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_everything(self.user1)
        self._assert_can_see_nothing(self.user2)

        # unassign view instance role to user1
        org1.remove_user_in_role(self.user1, self.role_view_instance)

        # only super can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)

    def test_get_queryset_instance_with_organization_default_role(self):
        """
        Test the organization default role
        """
        # No instances
        self._assert_can_see_nothing(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)
        self._assert_can_see_nothing(self.user3)

        # create a new request
        instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
        request1 = Support.objects.create(instance=instance1)
        self.assertTrue(request1 in Support.objects.all())
        self.assertEqual(Support.objects.count(), 1)

        # Add org1 into instance1 scopes
        org1 = Organization.objects.create(name="Organization #1")
        instance1.scopes.add(org1)

        # Add view instance to all organization's user
        org1.roles.add(self.role_view_instance)

        # No user in org1 so only superuser can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)
        self._assert_can_see_nothing(self.user3)

        # assign an empty role to user1 and user2
        org1.add_user_in_role(self.user1, self.empty_role)
        org1.add_user_in_role(self.user2, self.empty_role)

        # everyone can see except user3
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_everything(self.user1)
        self._assert_can_see_everything(self.user2)
        self._assert_can_see_nothing(self.user3)

        # remove user2 from org
        org1.remove_user_in_role(self.user2, self.empty_role)

        # user1 is still in organization
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_everything(self.user1)
        self._assert_can_see_nothing(self.user2)
        self._assert_can_see_nothing(self.user3)

        # Remove view instance to all organization's user
        org1.roles.remove(self.role_view_instance)

        # only super can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)
        self._assert_can_see_nothing(self.user3)

    def test_get_queryset_instance_on_team_instance_with_organization_role(self):
        """
        Test organization's role for Team instances
        """
        # No instances
        self._assert_can_see_nothing(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)

        # create a new request
        instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
        request1 = Support.objects.create(instance=instance1)
        self.assertTrue(request1 in Support.objects.all())
        self.assertEqual(Support.objects.count(), 1)

        # Add org1 into instance1 scopes
        org1 = Organization.objects.create(name="Organization #1")
        team1 = Team.objects.create(name="Team #1", org=org1)
        instance1.scopes.add(team1)

        # No user in org1 so only superuser can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)

        # assign role_view_instance to user1
        org1.add_user_in_role(self.user1, self.role_view_instance)

        # user1 can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_everything(self.user1)
        self._assert_can_see_nothing(self.user2)

        # Remove view instance to user1
        org1.remove_user_in_role(self.user1, self.role_view_instance)

        # only super can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)

    def test_get_queryset_instance_on_team_instance_with_organization_default_role(self):
        """
        Test organization's default role for Team instances
        """
        # No instances
        self._assert_can_see_nothing(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)
        self._assert_can_see_nothing(self.user3)

        # create a new request
        instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
        request1 = Support.objects.create(instance=instance1)
        self.assertTrue(request1 in Support.objects.all())
        self.assertEqual(Support.objects.count(), 1)

        # Add org1 into instance1 scopes
        org1 = Organization.objects.create(name="Organization #1")
        team1 = Team.objects.create(name="Team #1", org=org1)
        instance1.scopes.add(team1)

        # Add view instance to all organization's user
        org1.roles.add(self.role_view_instance)

        # No user in org1 so only superuser can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)
        self._assert_can_see_nothing(self.user3)

        # assign an empty role to user1 and user2
        org1.add_user_in_role(self.user1, self.empty_role)
        org1.add_user_in_role(self.user2, self.empty_role)

        # everyone can see except user3
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_everything(self.user1)
        self._assert_can_see_everything(self.user2)
        self._assert_can_see_nothing(self.user3)

        # remove user2 from org
        org1.remove_user_in_role(self.user2, self.empty_role)

        # user1 is still in organization
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_everything(self.user1)
        self._assert_can_see_nothing(self.user2)
        self._assert_can_see_nothing(self.user3)

        # Remove view instance to all organization's user
        org1.roles.remove(self.role_view_instance)

        # only super can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)
        self._assert_can_see_nothing(self.user3)

    ####################
    def test_get_queryset_instance_with_organization_role_with_quota_scope(self):
        """
        Test the organization's role
        """
        # No instances
        self._assert_can_see_nothing(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)

        # Create org1
        org1 = Organization.objects.create(name="Organization #1")

        # create a new instance with quota_scope set to org1
        instance1 = Instance.objects.create(name="Instance #1", quota_scope=org1)
        request1 = Support.objects.create(instance=instance1)
        self.assertTrue(request1 in Support.objects.all())
        self.assertEqual(Support.objects.count(), 1)

        # assign a view instance to user1
        org1.add_user_in_role(self.user1, self.role_view_instance)

        # everyone can see except user2
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_everything(self.user1)
        self._assert_can_see_nothing(self.user2)

        # unassign view instance role to user1
        org1.remove_user_in_role(self.user1, self.role_view_instance)

        # only super can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)

    def test_get_queryset_instance_with_organization_default_role_with_quota_scope(self):
        """
        Test the organization default role
        """
        # No instances
        self._assert_can_see_nothing(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)
        self._assert_can_see_nothing(self.user3)

        # Create org1
        org1 = Organization.objects.create(name="Organization #1")

        # create a new instance with quota_scope set to org1
        instance1 = Instance.objects.create(name="Instance #1", quota_scope=org1)
        request1 = Support.objects.create(instance=instance1)
        self.assertTrue(request1 in Support.objects.all())
        self.assertEqual(Support.objects.count(), 1)

        # Add view instance to all organization's user
        org1.roles.add(self.role_view_instance)

        # No user in org1 so only superuser can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)
        self._assert_can_see_nothing(self.user3)

        # assign an empty role to user1 and user2
        org1.add_user_in_role(self.user1, self.empty_role)
        org1.add_user_in_role(self.user2, self.empty_role)

        # everyone can see except user3
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_everything(self.user1)
        self._assert_can_see_everything(self.user2)
        self._assert_can_see_nothing(self.user3)

        # remove user2 from org
        org1.remove_user_in_role(self.user2, self.empty_role)

        # user1 is still in organization
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_everything(self.user1)
        self._assert_can_see_nothing(self.user2)
        self._assert_can_see_nothing(self.user3)

        # Remove view instance to all organization's user
        org1.roles.remove(self.role_view_instance)

        # only super can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)
        self._assert_can_see_nothing(self.user3)

    def test_get_queryset_instance_on_team_instance_with_organization_role_with_quota_scope(self):
        """
        Test organization's role for Team instances
        """
        # No instances
        self._assert_can_see_nothing(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)



        # Create org1 and team1
        org1 = Organization.objects.create(name="Organization #1")
        team1 = Team.objects.create(name="Team #1", org=org1)

        # create a new instance with quota_scope set to team1
        instance1 = Instance.objects.create(name="Instance #1", quota_scope=team1)
        request1 = Support.objects.create(instance=instance1)
        self.assertTrue(request1 in Support.objects.all())
        self.assertEqual(Support.objects.count(), 1)


        # No user in org1 so only superuser can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)

        # assign role_view_instance to user1
        org1.add_user_in_role(self.user1, self.role_view_instance)

        # user1 can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_everything(self.user1)
        self._assert_can_see_nothing(self.user2)

        # Remove view instance to user1
        org1.remove_user_in_role(self.user1, self.role_view_instance)

        # only super can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)

    def test_get_queryset_instance_on_team_instance_with_organization_default_role_with_quota_scope(self):
        """
        Test organization's default role for Team instances
        """
        # No instances
        self._assert_can_see_nothing(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)
        self._assert_can_see_nothing(self.user3)

        # Create org1 and team1
        org1 = Organization.objects.create(name="Organization #1")
        team1 = Team.objects.create(name="Team #1", org=org1)

        # create a new instance with quota_scope set to team1
        instance1 = Instance.objects.create(name="Instance #1", quota_scope=team1)
        request1 = Support.objects.create(instance=instance1)
        self.assertTrue(request1 in Support.objects.all())
        self.assertEqual(Support.objects.count(), 1)

        # Add view instance to all organization's user
        org1.roles.add(self.role_view_instance)

        # No user in org1 so only superuser can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)
        self._assert_can_see_nothing(self.user3)

        # assign an empty role to user1 and user2
        org1.add_user_in_role(self.user1, self.empty_role)
        org1.add_user_in_role(self.user2, self.empty_role)

        # everyone can see except user3
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_everything(self.user1)
        self._assert_can_see_everything(self.user2)
        self._assert_can_see_nothing(self.user3)

        # remove user2 from org
        org1.remove_user_in_role(self.user2, self.empty_role)

        # user1 is still in organization
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_everything(self.user1)
        self._assert_can_see_nothing(self.user2)
        self._assert_can_see_nothing(self.user3)

        # Remove view instance to all organization's user
        org1.roles.remove(self.role_view_instance)

        # only super can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)
        self._assert_can_see_nothing(self.user3)
