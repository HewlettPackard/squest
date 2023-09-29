from django.contrib.auth.models import User

from profiles.models import Team, Organization, GlobalScope, Role
from profiles.models.squest_permission import Permission

from service_catalog.models import Instance, Support
from tests.utils import TransactionTestUtils


class TestModelScopeGetQuerysetSupport(TransactionTestUtils):

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
        self.global_scope = GlobalScope.load()

    def _assert_can_see_everything(self, user):
        self.assertQuerysetEqualID(Support.get_queryset_for_user(user, self.permission),
                                   Support.objects.all())

    def _assert_can_see_nothing(self, user):
        self.assertQuerysetEqualID(Support.get_queryset_for_user(user, self.permission),
                                   Support.objects.none())

    def test_get_queryset_when_owner_instance(self):
        """
        Test the global_permissions in request permission
        """

        # No instances
        self._assert_can_see_nothing(self.superuser)
        self._assert_can_see_nothing(self.user1)

        # create a new request
        instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope,
                                            requester=self.user1)
        request1 = Support.objects.create(instance=instance1)
        self.assertTrue(request1 in Support.objects.all())
        self.assertEqual(Support.objects.count(), 1)

        # add global perm
        self.global_scope.owner_permissions.add(self.permission_object)

        # everyone can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_everything(self.user1)

        # remove global perm
        self.global_scope.owner_permissions.remove(self.permission_object)

        # only super can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_nothing(self.user1)

    def test_get_queryset_when_owner_support(self):
        """
        Test the global_permissions in request permission
        """

        # No instances
        self._assert_can_see_nothing(self.superuser)
        self._assert_can_see_nothing(self.user1)

        # create a new request
        instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
        request1 = Support.objects.create(instance=instance1, opened_by=self.user1)
        self.assertTrue(request1 in Support.objects.all())
        self.assertEqual(Support.objects.count(), 1)

        # add global perm
        self.global_scope.owner_permissions.add(self.permission_object)

        # everyone can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_everything(self.user1)

        # remove global perm
        self.global_scope.owner_permissions.remove(self.permission_object)

        # only super can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_nothing(self.user1)

    def test_get_queryset_globalscope_global_permissions(self):
        """
        Test the global_permissions in global scope
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
        self.global_scope.global_permissions.add(self.permission_object)

        # everyone can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_everything(self.user1)

        # remove global perm
        self.global_scope.global_permissions.remove(self.permission_object)

        # only super can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_nothing(self.user1)

    def test_get_queryset_globalscope_perm_specific_user(self):
        """
        Test the rbac role in global scope
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
        self.global_scope.add_user_in_role(self.user1, self.role_view_instance)

        # everyone can see except user2
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_everything(self.user1)
        self._assert_can_see_nothing(self.user2)

        # unassign view instance role to user1
        self.global_scope.remove_user_in_role(self.user1, self.role_view_instance)

        # only super can see
        self._assert_can_see_everything(self.superuser)
        self._assert_can_see_nothing(self.user1)
        self._assert_can_see_nothing(self.user2)

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
