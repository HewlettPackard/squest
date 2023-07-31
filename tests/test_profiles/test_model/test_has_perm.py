from django.contrib.auth.models import User

from profiles.models import Organization, GlobalPermission, Role, Team
from profiles.models.squest_permission import Permission

from service_catalog.models import Instance, Request, Operation, Service, JobTemplate, TowerServer, Support
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

        survey = {
            "name": "test-survey",
            "description": "test-survey-description",
            "spec": []
        }

        service = Service.objects.create(name="Service #1")
        tower = TowerServer.objects.create(name="Tower #1", host="localhost", token="xxx")

        job_template = JobTemplate.objects.create(name="Job Template #1", survey=survey,
                                                  tower_id=1,
                                                  tower_server=tower,
                                                  )

        self.operation = Operation.objects.create(name="Operation #1", service=service, job_template=job_template)

    def _get_action_perm(self, obj, action):
        return f"{obj.__class__._meta.app_label}.{action}_{obj.__class__._meta.model_name}"

    def _get_perm(self, obj, action):
        print(obj, action)
        return Permission.objects.get(content_type__app_label=f"{obj.__class__._meta.app_label}",
                                      content_type__model=f"{obj.__class__._meta.model_name}",
                                      codename=f"{action}_{obj.__class__._meta.model_name}")

    def _assert_user_can(self, action, user, obj):
        print(f"testing that {user} can {action} on {obj}")
        self.assertTrue(user.has_perm(self._get_action_perm(obj, action), obj))

    def _assert_user_cant(self, action, user, obj):
        print(f"testing that {user} cannot {action} on {obj}")
        self.assertFalse(user.has_perm(self._get_action_perm(obj, action), obj))

    def __test_has_perm_generic_with_global_perm_user_permission(self, obj, action):

        permission = self._get_perm(obj, action)

        # Only superuser can see
        self._assert_user_cant(action, self.user1, obj)
        self._assert_user_can(action, self.superuser, obj)

        # Add {action}_{object} to everyone
        self.global_perm.user_permissions.add(permission)

        # user1 can see it
        self._assert_user_can(action, self.user1, obj)
        self._assert_user_can(action, self.superuser, obj)

        # Remove view_instance to everyone
        self.global_perm.user_permissions.remove(permission)

        # Only superuser can see
        self._assert_user_cant(action, self.user1, obj)
        self._assert_user_can(action, self.superuser, obj)

    def test_has_perm_instance_global_user_perm(self):
        for action in ["add", "view", "change", "delete", "list"]:
            instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
            self.__test_has_perm_generic_with_global_perm_user_permission(instance1, action)

    def test_has_perm_request_global_user_perm(self):
        for action in ["add", "view", "change", "delete", "list"]:
            instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
            request1 = Request.objects.create(instance=instance1, operation=self.operation)
            self.__test_has_perm_generic_with_global_perm_user_permission(request1, action)

    def test_has_perm_support_global_user_perm(self):
        for action in ["add", "view", "change", "delete", "list"]:
            instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
            support1 = Support.objects.create(instance=instance1)
            self.__test_has_perm_generic_with_global_perm_user_permission(support1, action)

    def test_has_perm_org_global_user_perm(self):
        for action in ["add", "view", "change", "delete", "list"]:
            org1 = Organization.objects.create(name="Organization #1")
            self.__test_has_perm_generic_with_global_perm_user_permission(org1, action)

    def test_has_perm_team_global_user_perm(self):
        for action in ["add", "view", "change", "delete", "list"]:
            org1 = Organization.objects.create(name="Organization #1")
            team1 = Team.objects.create(name="Team #1", org=org1)
            self.__test_has_perm_generic_with_global_perm_user_permission(team1, action)

    def test_has_perm_globalperm_global_user_perm(self):
        for action in ["add", "view", "change", "delete", "list"]:
            self.__test_has_perm_generic_with_global_perm_user_permission(self.global_perm, action)

    def __test_has_perm_generic_with_global_perm_role(self, obj, action):

        permission = self._get_perm(obj, action)
        role = Role.objects.create(name=f"{action} on {obj.__class__._meta.model_name}")
        role.permissions.add(permission)

        # Only superuser can see
        self._assert_user_cant(action, self.user1, obj)
        self._assert_user_cant(action, self.user2, obj)
        self._assert_user_can(action, self.superuser, obj)

        # Add {action}_{object} to everyone
        self.global_perm.add_user_in_role(self.user1, role)

        # user1 can see it
        self._assert_user_can(action, self.user1, obj)
        self._assert_user_cant(action, self.user2, obj)
        self._assert_user_can(action, self.superuser, obj)

        # Remove view_instance to everyone
        self.global_perm.remove_user_in_role(self.user1, role)

        # Only superuser can see
        self._assert_user_cant(action, self.user1, obj)
        self._assert_user_cant(action, self.user1, obj)
        self._assert_user_can(action, self.superuser, obj)

    def test_has_perm_instance_global_perm_role(self):
        for action in ["add", "view", "change", "delete", "list"]:
            instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
            self.__test_has_perm_generic_with_global_perm_role(instance1, action)

    def test_has_perm_request_global_perm_role(self):
        for action in ["add", "view", "change", "delete", "list"]:
            instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
            request1 = Request.objects.create(instance=instance1, operation=self.operation)
            self.__test_has_perm_generic_with_global_perm_role(request1, action)

    def test_has_perm_support_global_perm_role(self):
        for action in ["add", "view", "change", "delete", "list"]:
            instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
            support1 = Support.objects.create(instance=instance1)
            self.__test_has_perm_generic_with_global_perm_role(support1, action)

    def test_has_perm_org_global_perm_role(self):
        for action in ["add", "view", "change", "delete", "list"]:
            org1 = Organization.objects.create(name="Organization #1")
            self.__test_has_perm_generic_with_global_perm_role(org1, action)

    def test_has_perm_team_global_perm_role(self):
        for action in ["add", "view", "change", "delete", "list"]:
            org1 = Organization.objects.create(name="Organization #1")
            team1 = Team.objects.create(name="Team #1", org=org1)
            self.__test_has_perm_generic_with_global_perm_role(team1, action)

    def test_has_perm_globalperm_global_perm_role(self):
        for action in ["add", "view", "change", "delete", "list"]:
            self.__test_has_perm_generic_with_global_perm_role(self.global_perm, action)

    def __test_has_perm_generic_with_scope_role(self, obj, action, scope):

        permission = self._get_perm(obj, action)
        role = Role.objects.create(name=f"{action} on {obj.__class__._meta.model_name}")
        role.permissions.add(permission)

        # Only superuser can see
        self._assert_user_cant(action, self.user1, obj)
        self._assert_user_cant(action, self.user2, obj)
        self._assert_user_can(action, self.superuser, obj)

        # Add {action}_{object} to everyone
        scope.add_user_in_role(self.user1, role)

        # user1 can see it
        self._assert_user_can(action, self.user1, obj)
        self._assert_user_cant(action, self.user2, obj)
        self._assert_user_can(action, self.superuser, obj)

        # Remove view_instance to everyone
        scope.remove_user_in_role(self.user1, role)

        # Only superuser can see
        self._assert_user_cant(action, self.user1, obj)
        self._assert_user_cant(action, self.user1, obj)
        self._assert_user_can(action, self.superuser, obj)

    def test_has_perm_instance_org_role(self):
        for action in ["add", "view", "change", "delete", "list"]:
            instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
            self.__test_has_perm_generic_with_scope_role(instance1, action, instance1.quota_scope)

    def test_has_perm_request_org_role(self):
        for action in ["add", "view", "change", "delete", "list"]:
            instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
            request1 = Request.objects.create(instance=instance1, operation=self.operation)
            self.__test_has_perm_generic_with_scope_role(request1, action, request1.instance.quota_scope)

    def test_has_perm_support_org_role(self):
        for action in ["add", "view", "change", "delete", "list"]:
            instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
            support1 = Support.objects.create(instance=instance1)
            self.__test_has_perm_generic_with_scope_role(support1, action, support1.instance.quota_scope)

    def test_has_perm_org_org_role(self):
        for action in ["add", "view", "change", "delete", "list"]:
            org1 = Organization.objects.create(name="Organization #1")
            self.__test_has_perm_generic_with_scope_role(org1, action, org1)

    def test_has_perm_team_org_role(self):
        for action in ["add", "view", "change", "delete", "list"]:
            org1 = Organization.objects.create(name="Organization #1")
            team1 = Team.objects.create(name="Team #1", org=org1)
            self.__test_has_perm_generic_with_scope_role(team1, action, org1)

    def test_has_perm_team_team_role(self):
        for action in ["add", "view", "change", "delete", "list"]:
            org1 = Organization.objects.create(name="Organization #1")
            team1 = Team.objects.create(name="Team #1", org=org1)
            org1.add_user_in_role(self.user1, self.empty_role)
            self.__test_has_perm_generic_with_scope_role(team1, action, team1)

    def __test_has_perm_generic_with_scope_role(self, obj, action, scope):

        permission = self._get_perm(obj, action)
        role = Role.objects.create(name=f"{action} on {obj.__class__._meta.model_name}")
        role.permissions.add(permission)

        # Only superuser can see
        self._assert_user_cant(action, self.user1, obj)
        self._assert_user_cant(action, self.user2, obj)
        self._assert_user_can(action, self.superuser, obj)

        # Add {action}_{object} to everyone
        scope.add_user_in_role(self.user1, role)

        # user1 can see it
        self._assert_user_can(action, self.user1, obj)
        self._assert_user_cant(action, self.user2, obj)
        self._assert_user_can(action, self.superuser, obj)

        # Remove view_instance to everyone
        scope.remove_user_in_role(self.user1, role)

        # Only superuser can see
        self._assert_user_cant(action, self.user1, obj)
        self._assert_user_cant(action, self.user1, obj)
        self._assert_user_can(action, self.superuser, obj)

    def test_has_perm_instance_org_role(self):
        for action in ["add", "view", "change", "delete", "list"]:
            instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
            self.__test_has_perm_generic_with_scope_role(instance1, action, instance1.quota_scope)

    def test_has_perm_request_org_role(self):
        for action in ["add", "view", "change", "delete", "list"]:
            instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
            request1 = Request.objects.create(instance=instance1, operation=self.operation)
            self.__test_has_perm_generic_with_scope_role(request1, action, request1.instance.quota_scope)

    def test_has_perm_support_org_role(self):
        for action in ["add", "view", "change", "delete", "list"]:
            instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
            support1 = Support.objects.create(instance=instance1)
            self.__test_has_perm_generic_with_scope_role(support1, action, support1.instance.quota_scope)

    def __test_has_perm_generic_with_org_default_role(self, obj, action, scope):

        permission = self._get_perm(obj, action)
        role = Role.objects.create(name=f"{action} on {obj.__class__._meta.model_name}")
        role.permissions.add(permission)

        # Only superuser can see
        self._assert_user_cant(action, self.user1, obj)
        self._assert_user_cant(action, self.user2, obj)
        self._assert_user_cant(action, self.user3, obj)
        self._assert_user_can(action, self.superuser, obj)

        # Empty role to user1 so he can't see
        scope.add_user_in_role(self.user1, self.empty_role)

        # Only superuser can see
        self._assert_user_cant(action, self.user1, obj)
        self._assert_user_cant(action, self.user2, obj)
        self._assert_user_cant(action, self.user3, obj)
        self._assert_user_can(action, self.superuser, obj)

        # Add {action}_{object} to everyone -> user 1 will have it as he is in org
        scope.roles.add(role)

        # user1 can see it
        self._assert_user_can(action, self.user1, obj)
        self._assert_user_cant(action, self.user2, obj)
        self._assert_user_cant(action, self.user3, obj)
        self._assert_user_can(action, self.superuser, obj)

        scope.add_user_in_role(self.user2, self.empty_role)

        # user1 and user2 can see it
        self._assert_user_can(action, self.user1, obj)
        self._assert_user_can(action, self.user2, obj)
        self._assert_user_cant(action, self.user3, obj)
        self._assert_user_can(action, self.superuser, obj)

        # Remove user2 from org
        scope.remove_user_in_role(self.user2, self.empty_role)

        # only user1 can see it
        self._assert_user_can(action, self.user1, obj)
        self._assert_user_cant(action, self.user2, obj)
        self._assert_user_cant(action, self.user3, obj)
        self._assert_user_can(action, self.superuser, obj)

        # Remove {action}_{object} to everyone
        scope.roles.remove(role)

        # Only superuser can see
        self._assert_user_cant(action, self.user1, obj)

        self._assert_user_cant(action, self.user2, obj)
        self._assert_user_cant(action, self.user3, obj)

        self._assert_user_can(action, self.superuser, obj)

    def test_has_perm_instance_org_default_role(self):
        for action in ["add", "view", "change", "delete", "list"]:
            instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
            self.__test_has_perm_generic_with_org_default_role(instance1, action, instance1.quota_scope)

    def test_has_perm_request_org_default_role(self):
        for action in ["add", "view", "change", "delete", "list"]:
            instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
            request1 = Request.objects.create(instance=instance1, operation=self.operation)
            self.__test_has_perm_generic_with_org_default_role(request1, action, request1.instance.quota_scope)

    def test_has_perm_support_org_default_role(self):
        for action in ["add", "view", "change", "delete", "list"]:
            instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
            support1 = Support.objects.create(instance=instance1)
            self.__test_has_perm_generic_with_org_default_role(support1, action, support1.instance.quota_scope)
