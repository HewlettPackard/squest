from django.contrib.auth.models import User

from profiles.models import Organization, GlobalScope, Role, Team
from profiles.models.squest_permission import Permission
from service_catalog.models import TowerServer

from tests.utils import TransactionTestUtils


class TestModelWhoHasPermOnOtherModel(TransactionTestUtils):
    # This part tests who_has_perm with objects not related to Instance (e.g TowerServer)
    def setUp(self):
        super(TestModelWhoHasPermOnOtherModel, self).setUp()

        self.global_scope = GlobalScope.load()
        self.empty_role = Role.objects.create(name="Empty role")

        self.test_org = Organization.objects.create(name="Org")
        self.test_team = Team.objects.create(name="Team", org=self.test_org)

        self.view_tower_server = Permission.objects.get_by_natural_key(
            codename="view_towerserver",
            app_label="service_catalog",
            model="towerserver"
        )
        self.view_tower_server_role = Role.objects.create(name="View instance role")
        self.view_tower_server_role.permissions.add(self.view_tower_server)

        self.tower_server = TowerServer.objects.create(name="tower-server-test-2", host="my-tower.com",
                                                       token="xxx")

        self.user = User.objects.create_user('user', 'user@hpe.com', "password")
        self.user_with_no_perm = User.objects.create_user('user_with_no_perm', 'user_with_no_perm@hpe.com', "password")
        self.superuser = User.objects.create_superuser(username='superuser')

    def test_who_has_perm_on_tower_server_superuser(self):
        # No permissions given, only superuser has perm
        user_with_permissions = self.tower_server.who_has_perm("service_catalog.view_towerserver")
        self.assertQuerysetEqualID(user_with_permissions, User.objects.filter(is_superuser=True))
        self.assertNotIn(self.user_with_no_perm, user_with_permissions)

    def test_who_has_perm_on_tower_server_global_scope_global_permissions(self):
        # user_with_permissions is empty
        user_with_permissions = self.tower_server.who_has_perm("service_catalog.view_towerserver")
        self.assertQuerysetEqualID(user_with_permissions, User.objects.filter(is_superuser=True))
        self.assertNotIn(self.user_with_no_perm, user_with_permissions)

        # Permission given in GlobalScope as global_permissions
        self.global_scope.global_permissions.add(self.view_tower_server)

        # Permissions given to all Squest user
        user_with_permissions = self.tower_server.who_has_perm("service_catalog.view_towerserver")
        self.assertQuerysetEqualID(user_with_permissions, User.objects.all())
        self.assertIn(self.user_with_no_perm, user_with_permissions)

    def test_who_has_perm_on_tower_server_global_scope_rbac(self):
        # Test Team RBAC
        ## user is not in Team
        user_with_permissions = self.tower_server.who_has_perm("service_catalog.view_towerserver")
        self.assertNotIn(self.user, user_with_permissions)
        self.assertNotIn(self.user_with_no_perm, user_with_permissions)

        ## Add view_tower_server_role in global_scope for self.user
        self.global_scope.add_user_in_role(self.user, self.view_tower_server_role)

        ## user is now in the list
        user_with_permissions = self.tower_server.who_has_perm("service_catalog.view_towerserver")
        self.assertIn(self.user, user_with_permissions)
        self.assertNotIn(self.user_with_no_perm, user_with_permissions)
