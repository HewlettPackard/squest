from django.contrib.auth.models import User, Permission
from profiles.models import Organization, GlobalPermission, Role

from tests.utils import TransactionTestUtils


class TestModelHasPerm(TransactionTestUtils):

    def setUp(self):
        super(TestModelHasPerm, self).setUp()
        self.default_quota_scope = Organization.objects.create(name="Default scope for tests")

        self.user1 = User.objects.create_user('user1', 'user1@hpe.com', "password")
        self.user2 = User.objects.create_user('user2', 'user2@hpe.com', "password")
        self.user3 = User.objects.create_user('user3', 'user3@hpe.com', "password")
        self.superuser = User.objects.create_superuser("superuser")

        self.empty_role = Role.objects.create(name="Empty role")

        self.global_perm = GlobalPermission.load()
        self.global_perm.user_permissions.set([])

    def _get_action_perm(self, obj_class, action):
        return f"{obj_class._meta.app_label}.{action}_{obj_class._meta.model_name}"

    def _get_perm(self, obj_class, action):
        return Permission.objects.get(content_type__app_label=f"{obj_class._meta.app_label}",
                                      content_type__model=f"{obj_class._meta.model_name}",
                                      codename=f"{action}_{obj_class._meta.model_name}")

    def _assert_user_can(self, action, user, obj_class):
        print(f"testing that {user} can {action} on {obj_class}")
        self.assertTrue(user.has_perm(self._get_action_perm(obj_class, action)))

    def _assert_user_cant(self, action, user, obj_class):
        print(f"testing that {user} cannot {action} on {obj_class}")
        self.assertFalse(user.has_perm(self._get_action_perm(obj_class, action)))

    def __test_has_perm_generic_with_global_perm_user_permission(self, obj_class, action):

        permission = self._get_perm(obj_class, action)

        # Only superuser can see
        self._assert_user_cant(action, self.user1, obj_class)
        self._assert_user_can(action, self.superuser, obj_class)

        # Add {action}_{object} to everyone
        self.global_perm.user_permissions.add(permission)

        # user1 can see it
        self._assert_user_can(action, self.user1, obj_class)
        self._assert_user_can(action, self.superuser, obj_class)

        # Remove view_instance to everyone
        self.global_perm.user_permissions.remove(permission)

        # Only superuser can see
        self._assert_user_cant(action, self.user1, obj_class)
        self._assert_user_can(action, self.superuser, obj_class)

    def test_has_perm_instance_global_user_perm(self):
        for action in ["add", "view", "change", "delete"]:
            self.__test_has_perm_generic_with_global_perm_user_permission(Permission, action)

    def __test_has_perm_generic_with_global_perm_role(self, obj_class, action):

        permission = self._get_perm(obj_class, action)
        role = Role.objects.create(name=f"{action} on {obj_class._meta.model_name}")
        role.permissions.add(permission)

        # Only superuser can see
        self._assert_user_cant(action, self.user1, obj_class)
        self._assert_user_cant(action, self.user2, obj_class)
        self._assert_user_can(action, self.superuser, obj_class)

        # Add {action}_{object} to everyone
        self.global_perm.add_user_in_role(self.user1, role)

        # user1 can see it
        self._assert_user_can(action, self.user1, obj_class)
        self._assert_user_cant(action, self.user2, obj_class)
        self._assert_user_can(action, self.superuser, obj_class)

        # Remove view_instance to everyone
        self.global_perm.remove_user_in_role(self.user1, role)

        # Only superuser can see
        self._assert_user_cant(action, self.user1, obj_class)
        self._assert_user_cant(action, self.user1, obj_class)
        self._assert_user_can(action, self.superuser, obj_class)

    def test_has_perm_instance_global_perm_role(self):
        for action in ["add", "view", "change", "delete"]:
            self.__test_has_perm_generic_with_global_perm_role(Permission, action)
