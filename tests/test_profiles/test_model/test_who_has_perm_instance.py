from django.contrib.auth.models import User

from profiles.models import Organization, GlobalPermission, Role, Team
from profiles.models.squest_permission import Permission
from service_catalog.models import Instance

from tests.utils import TransactionTestUtils


class TestModelWhoHasPermOnModelLinkedToInstances(TransactionTestUtils):
    # This part tests who_has_perm with objects related to Instance (e.g Request)
    def setUp(self):
        super(TestModelWhoHasPermOnModelLinkedToInstances, self).setUp()

        self.global_perm = GlobalPermission.load()
        self.empty_role = Role.objects.create(name="Empty role")

        self.test_org = Organization.objects.create(name="Org")
        self.test_team = Team.objects.create(name="Team", org=self.test_org)

        self.view_instance_permission = Permission.objects.get_by_natural_key(
            codename="view_instance",
            app_label="service_catalog",
            model="instance"
        )
        self.view_instance_role = Role.objects.create(name="View instance role")
        self.view_instance_role.permissions.add(self.view_instance_permission)

        self.instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.test_team)

        self.user = User.objects.create_user('user', 'user@hpe.com', "password")
        self.user_with_no_perm = User.objects.create_user('user_with_no_perm', 'user_with_no_perm@hpe.com', "password")
        self.superuser = User.objects.create_superuser(username='superuser')

    def test_who_has_perm_on_instance_superuser(self):
        # No permissions given, only superuser has perm
        user_with_permissions = self.instance1.who_has_perm('service_catalog.view_instance')
        self.assertQuerysetEqualID(user_with_permissions, User.objects.filter(is_superuser=True))
        self.assertNotIn(self.user_with_no_perm, user_with_permissions)

    def test_who_has_perm_on_instance_globalperm_default_permissions(self):
        # user_with_permissions is empty
        user_with_permissions = self.instance1.who_has_perm('service_catalog.view_instance')
        self.assertQuerysetEqualID(user_with_permissions, User.objects.filter(is_superuser=True))
        self.assertNotIn(self.user_with_no_perm, user_with_permissions)

        # Permission given in GlobalPerm as default_permissions
        self.global_perm.default_permissions.add(self.view_instance_permission)

        # Permissions given to all Squest user
        user_with_permissions = self.instance1.who_has_perm('service_catalog.view_instance')
        self.assertQuerysetEqualID(user_with_permissions, User.objects.all())
        self.assertIn(self.user_with_no_perm, user_with_permissions)

    def test_who_has_perm_on_instance_team_roles(self):
        # Test Team.roles
        ## user is not in Team
        user_with_permissions = self.instance1.who_has_perm('service_catalog.view_instance')
        self.assertNotIn(self.user, user_with_permissions)
        self.assertNotIn(self.user_with_no_perm, user_with_permissions)

        ## add user in org with empty role
        self.test_org.add_user_in_role(self.user, self.empty_role)
        self.test_team.add_user_in_role(self.user, self.empty_role)

        ## user is in Team but no default roles
        user_with_permissions = self.instance1.who_has_perm('service_catalog.view_instance')
        self.assertNotIn(self.user, user_with_permissions)
        self.assertNotIn(self.user_with_no_perm, user_with_permissions)

        ## Add view_instance_role in test_team for all users
        self.test_team.roles.add(self.view_instance_role)

        ## user is now in the list
        user_with_permissions = self.instance1.who_has_perm('service_catalog.view_instance')
        self.assertIn(self.user, user_with_permissions)
        self.assertNotIn(self.user_with_no_perm, user_with_permissions)

    def test_who_has_perm_on_instance_org_roles(self):
        # Test Org.roles
        ## user is not in Org
        user_with_permissions = self.instance1.who_has_perm('service_catalog.view_instance')
        self.assertNotIn(self.user, user_with_permissions)
        self.assertNotIn(self.user_with_no_perm, user_with_permissions)

        ## add user in org with empty role
        self.test_org.add_user_in_role(self.user, self.empty_role)

        ## user is in Org but no default roles
        user_with_permissions = self.instance1.who_has_perm('service_catalog.view_instance')
        self.assertNotIn(self.user, user_with_permissions)
        self.assertNotIn(self.user_with_no_perm, user_with_permissions)

        ## Add view_instance_role in test_org for all users
        self.test_org.roles.add(self.view_instance_role)

        ## user is now in the list
        user_with_permissions = self.instance1.who_has_perm('service_catalog.view_instance')
        self.assertIn(self.user, user_with_permissions)
        self.assertNotIn(self.user_with_no_perm, user_with_permissions)

    def test_who_has_perm_on_instance_org_rbac(self):
        # Test Org RBAC
        ## user is not in Org
        user_with_permissions = self.instance1.who_has_perm('service_catalog.view_instance')
        self.assertNotIn(self.user, user_with_permissions)
        self.assertNotIn(self.user_with_no_perm, user_with_permissions)

        ## Add view_instance_role in test_org for self.user
        self.test_org.add_user_in_role(self.user, self.view_instance_role)

        ## user is now in the list
        user_with_permissions = self.instance1.who_has_perm('service_catalog.view_instance')
        self.assertIn(self.user, user_with_permissions)
        self.assertNotIn(self.user_with_no_perm, user_with_permissions)

    def test_who_has_perm_on_instance_team_rbac(self):
        # Test Team RBAC
        ## user is not in Team
        user_with_permissions = self.instance1.who_has_perm('service_catalog.view_instance')
        self.assertNotIn(self.user, user_with_permissions)
        self.assertNotIn(self.user_with_no_perm, user_with_permissions)

        ## Add view_instance_role in test_org for self.user
        self.test_org.add_user_in_role(self.user, self.empty_role)
        self.test_team.add_user_in_role(self.user, self.view_instance_role)

        ## user is now in the list
        user_with_permissions = self.instance1.who_has_perm('service_catalog.view_instance')
        self.assertIn(self.user, user_with_permissions)
        self.assertNotIn(self.user_with_no_perm, user_with_permissions)

    def test_who_has_perm_on_instance_globalperm_rbac(self):
        # Test Team RBAC
        ## user is not in Team
        user_with_permissions = self.instance1.who_has_perm('service_catalog.view_instance')
        self.assertNotIn(self.user, user_with_permissions)
        self.assertNotIn(self.user_with_no_perm, user_with_permissions)

        ## Add view_instance_role in globalperm for self.user
        self.global_perm.add_user_in_role(self.user, self.view_instance_role)

        ## user is now in the list
        user_with_permissions = self.instance1.who_has_perm('service_catalog.view_instance')
        self.assertIn(self.user, user_with_permissions)
        self.assertNotIn(self.user_with_no_perm, user_with_permissions)
