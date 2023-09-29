from django.contrib.auth.models import User

from profiles.models import Organization, GlobalScope, Role
from profiles.models.squest_permission import Permission

from service_catalog.models import Instance, Request, Operation, Service, JobTemplate, TowerServer, Support
from tests.utils import TransactionTestUtils


class TestModelHasPermWithIsOwner(TransactionTestUtils):

    def setUp(self):
        super(TestModelHasPermWithIsOwner, self).setUp()
        self.default_quota_scope = Organization.objects.create(name="Default scope for tests")

        self.user1 = User.objects.create_user('user1', 'user1@hpe.com', "password")
        self.superuser = User.objects.create_superuser("superuser")

        self.requester_perm = GlobalScope.load()
        self.requester_perm.owner_permissions.set([])

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

    def __test_has_perm_generic_with_requester_perm_user_permission(self, obj, action):

        permission = self._get_perm(obj, action)

        # Only superuser can see
        self._assert_user_cant(action, self.user1, obj)
        self._assert_user_can(action, self.superuser, obj)

        # Add {action}_{object} to the owner
        self.requester_perm.owner_permissions.add(permission)

        # user1 can see it
        self._assert_user_can(action, self.user1, obj)
        self._assert_user_can(action, self.superuser, obj)

        # Remove view_instance to the owner
        self.requester_perm.owner_permissions.remove(permission)

        # Only superuser can see
        self._assert_user_cant(action, self.user1, obj)
        self._assert_user_can(action, self.superuser, obj)

    def test_has_perm_instance_requesterperm_when_instance_owner(self):
        for action in ["add", "view", "change", "delete"]:
            instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope,
                                                requester=self.user1)
            self.__test_has_perm_generic_with_requester_perm_user_permission(instance1, action)

    def test_has_perm_request_requesterperm_when_request_owner(self):
        for action in ["add", "view", "change", "delete"]:
            instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
            request1 = Request.objects.create(instance=instance1, operation=self.operation, user=self.user1)
            self.__test_has_perm_generic_with_requester_perm_user_permission(request1, action)

    def test_has_perm_request_requesterperm_when_instance_owner(self):
        for action in ["add", "view", "change", "delete"]:
            instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope,
                                                requester=self.user1)
            request1 = Request.objects.create(instance=instance1, operation=self.operation)
            self.__test_has_perm_generic_with_requester_perm_user_permission(request1, action)

    def test_has_perm_support_requesterperm_when_support_owner(self):
        for action in ["add", "view", "change", "delete"]:
            instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope)
            support1 = Support.objects.create(instance=instance1, opened_by=self.user1)
            self.__test_has_perm_generic_with_requester_perm_user_permission(support1, action)

    def test_has_perm_support_requesterperm_when_instance_owner(self):
        for action in ["add", "view", "change", "delete"]:
            instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.default_quota_scope,
                                                requester=self.user1)
            support1 = Support.objects.create(instance=instance1)
            self.__test_has_perm_generic_with_requester_perm_user_permission(support1, action)
