from django.contrib.auth.models import User

from profiles.models import Organization, GlobalScope
from profiles.models.squest_permission import Permission
from service_catalog.models import Instance, Request, Operation, Service, TowerServer, JobTemplate, Support, \
    SupportMessage, RequestMessage
from django.test import TestCase


class TestModelWhoHasPermOwnerOnModelLinkedToInstances(TestCase):
    # This part tests who_has_perm with objects related to Instance (e.g Request)
    def setUp(self):
        super(TestModelWhoHasPermOwnerOnModelLinkedToInstances, self).setUp()

        self.global_scope = GlobalScope.load()

        self.test_org = Organization.objects.create(name="Org")

        self.user = User.objects.create_user('user', 'user@hpe.com', "password")
        self.user_with_no_perm = User.objects.create_user('user_with_no_perm', 'user_with_no_perm@hpe.com', "password")
        self.superuser = User.objects.create_superuser(username='superuser')

        survey = {
            "name": "test-survey",
            "description": "test-survey-description",
            "spec": []
        }

        service = Service.objects.create(name="Service #1")
        tower = TowerServer.objects.create(name="Tower #1", host="localhost", token="xxx")
        job_template = JobTemplate.objects.create(
            name="Job Template #1",
            survey=survey,
            tower_id=1,
            tower_server=tower,
        )

        self.operation = Operation.objects.create(name="Operation #1", service=service, job_template=job_template)

    def _test_who_has_perm_generic(self, permission, squest_object):
        # Remove all owner_permissions
        GlobalScope.load().owner_permissions.set([])

        ## user is not in Team
        user_with_permissions = squest_object.who_has_perm(permission.permission_str)
        self.assertNotIn(self.user, user_with_permissions)
        self.assertNotIn(self.user_with_no_perm, user_with_permissions)
        self.assertIn(self.superuser, user_with_permissions)

        ## Add view_instance_role in owner_permissions
        GlobalScope.load().owner_permissions.add(permission)

        ## user is now in the list
        user_with_permissions = squest_object.who_has_perm(permission.permission_str)
        self.assertIn(self.user, user_with_permissions)
        self.assertNotIn(self.user_with_no_perm, user_with_permissions)
        self.assertIn(self.superuser, user_with_permissions)

    def _test_who_has_perm_generic_without_resetting_owner_perm(self, permission, squest_object):
        ## user is now in the list
        user_with_permissions = squest_object.who_has_perm(permission.permission_str)
        self.assertIn(self.user, user_with_permissions)
        self.assertNotIn(self.user_with_no_perm, user_with_permissions)
        self.assertIn(self.superuser, user_with_permissions)

    def test_who_has_perm_on_instance_global_scope_owner_permissions(self):
        permission = Permission.objects.get_by_natural_key(
            codename="view_instance",
            app_label="service_catalog",
            model="instance"
        )
        self.instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.test_org, requester=self.user)
        self._test_who_has_perm_generic(permission, self.instance1)

    def test_who_has_perm_on_request_global_scope_owner_permissions(self):
        permission = Permission.objects.get_by_natural_key(
            codename="view_request",
            app_label="service_catalog",
            model="request"
        )

        self.instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.test_org, requester=self.user)
        self.request1 = Request.objects.create(instance=self.instance1, operation=self.operation)
        self._test_who_has_perm_generic(permission, self.request1)

    def test_who_has_perm_on_request_global_scope_owner_permissions2(self):
        permission = Permission.objects.get_by_natural_key(
            codename="view_request",
            app_label="service_catalog",
            model="request"
        )
        self.instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.test_org)
        self.request1 = Request.objects.create(instance=self.instance1, operation=self.operation, user=self.user)
        self._test_who_has_perm_generic(permission, self.request1)

    def test_who_has_perm_on_support_global_scope_owner_permissions(self):
        permission = Permission.objects.get_by_natural_key(
            codename="view_support",
            app_label="service_catalog",
            model="support"
        )

        self.instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.test_org, requester=self.user)
        self.support1 = Support.objects.create(instance=self.instance1)
        self._test_who_has_perm_generic(permission, self.support1)

    def test_who_has_perm_on_support_global_scope_owner_permissions2(self):
        permission = Permission.objects.get_by_natural_key(
            codename="view_support",
            app_label="service_catalog",
            model="support"
        )
        self.instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.test_org)
        self.support1 = Support.objects.create(instance=self.instance1, opened_by=self.user)
        self._test_who_has_perm_generic(permission, self.support1)

    def test_who_has_perm_on_supportmessage_global_scope_owner_permissions(self):
        permission = Permission.objects.get_by_natural_key(
            codename="view_supportmessage",
            app_label="service_catalog",
            model="supportmessage"
        )

        self.instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.test_org, requester=self.user)
        self.support1 = Support.objects.create(instance=self.instance1)
        self.supportmessage1 = SupportMessage.objects.create(support=self.support1)
        self._test_who_has_perm_generic(permission, self.supportmessage1)

    def test_who_has_perm_on_supportmessage_global_scope_owner_permissions2(self):
        permission = Permission.objects.get_by_natural_key(
            codename="view_supportmessage",
            app_label="service_catalog",
            model="supportmessage"
        )

        self.instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.test_org)
        self.support1 = Support.objects.create(instance=self.instance1, opened_by=self.user)
        self.supportmessage1 = SupportMessage.objects.create(support=self.support1)
        self._test_who_has_perm_generic(permission, self.supportmessage1)

    def test_who_has_perm_on_supportmessage_global_scope_owner_permissions3(self):
        permission = Permission.objects.get_by_natural_key(
            codename="view_supportmessage",
            app_label="service_catalog",
            model="supportmessage"
        )

        self.instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.test_org)
        self.support1 = Support.objects.create(instance=self.instance1)
        self.supportmessage1 = SupportMessage.objects.create(support=self.support1, sender=self.user)
        self._test_who_has_perm_generic(permission, self.supportmessage1)

    def test_who_has_perm_on_requestmessage_global_scope_owner_permissions(self):
        permission = Permission.objects.get_by_natural_key(
            codename="view_requestmessage",
            app_label="service_catalog",
            model="requestmessage"
        )

        self.instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.test_org, requester=self.user)
        self.request1 = Request.objects.create(instance=self.instance1, operation=self.operation)
        self.requestmessage1 = RequestMessage.objects.create(request=self.request1)
        self._test_who_has_perm_generic(permission, self.requestmessage1)

    def test_who_has_perm_on_requestmessage_global_scope_owner_permissions2(self):
        permission = Permission.objects.get_by_natural_key(
            codename="view_requestmessage",
            app_label="service_catalog",
            model="requestmessage"
        )

        self.instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.test_org)
        self.request1 = Request.objects.create(instance=self.instance1, user=self.user, operation=self.operation)
        self.requestmessage1 = RequestMessage.objects.create(request=self.request1)
        self._test_who_has_perm_generic(permission, self.requestmessage1)

    def test_who_has_perm_on_requestmessage_global_scope_owner_permissions3(self):
        permission = Permission.objects.get_by_natural_key(
            codename="view_requestmessage",
            app_label="service_catalog",
            model="requestmessage"
        )

        self.instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.test_org)
        self.request1 = Request.objects.create(instance=self.instance1, operation=self.operation)
        self.requestmessage1 = RequestMessage.objects.create(request=self.request1, sender=self.user)
        self._test_who_has_perm_generic(permission, self.requestmessage1)

    def test_without_resetting_perms_who_has_perm_on_instance_global_scope_owner_permissions(self):
        permission = Permission.objects.get_by_natural_key(
            codename="view_instance",
            app_label="service_catalog",
            model="instance"
        )
        self.instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.test_org, requester=self.user)
        self._test_who_has_perm_generic_without_resetting_owner_perm(permission, self.instance1)

    def test_without_resetting_perms_who_has_perm_on_request_global_scope_owner_permissions(self):
        permission = Permission.objects.get_by_natural_key(
            codename="view_request",
            app_label="service_catalog",
            model="request"
        )

        self.instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.test_org, requester=self.user)
        self.request1 = Request.objects.create(instance=self.instance1, operation=self.operation)
        self._test_who_has_perm_generic_without_resetting_owner_perm(permission, self.request1)

    def test_without_resetting_perms_who_has_perm_on_request_global_scope_owner_permissions2(self):
        permission = Permission.objects.get_by_natural_key(
            codename="view_request",
            app_label="service_catalog",
            model="request"
        )
        self.instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.test_org)
        self.request1 = Request.objects.create(instance=self.instance1, operation=self.operation, user=self.user)
        self._test_who_has_perm_generic_without_resetting_owner_perm(permission, self.request1)

    def test_without_resetting_perms_who_has_perm_on_support_global_scope_owner_permissions(self):
        permission = Permission.objects.get_by_natural_key(
            codename="view_support",
            app_label="service_catalog",
            model="support"
        )

        self.instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.test_org, requester=self.user)
        self.support1 = Support.objects.create(instance=self.instance1)
        self._test_who_has_perm_generic_without_resetting_owner_perm(permission, self.support1)

    def test_without_resetting_perms_who_has_perm_on_support_global_scope_owner_permissions2(self):
        permission = Permission.objects.get_by_natural_key(
            codename="view_support",
            app_label="service_catalog",
            model="support"
        )
        self.instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.test_org)
        self.support1 = Support.objects.create(instance=self.instance1, opened_by=self.user)
        self._test_who_has_perm_generic_without_resetting_owner_perm(permission, self.support1)

    def test_without_resetting_perms_who_has_perm_on_supportmessage_global_scope_owner_permissions(self):
        permission = Permission.objects.get_by_natural_key(
            codename="view_supportmessage",
            app_label="service_catalog",
            model="supportmessage"
        )

        self.instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.test_org, requester=self.user)
        self.support1 = Support.objects.create(instance=self.instance1)
        self.supportmessage1 = SupportMessage.objects.create(support=self.support1)
        self._test_who_has_perm_generic_without_resetting_owner_perm(permission, self.supportmessage1)

    def test_without_resetting_perms_who_has_perm_on_supportmessage_global_scope_owner_permissions2(self):
        permission = Permission.objects.get_by_natural_key(
            codename="view_supportmessage",
            app_label="service_catalog",
            model="supportmessage"
        )

        self.instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.test_org)
        self.support1 = Support.objects.create(instance=self.instance1, opened_by=self.user)
        self.supportmessage1 = SupportMessage.objects.create(support=self.support1)
        self._test_who_has_perm_generic_without_resetting_owner_perm(permission, self.supportmessage1)

    def test_without_resetting_perms_who_has_perm_on_supportmessage_global_scope_owner_permissions3(self):
        permission = Permission.objects.get_by_natural_key(
            codename="view_supportmessage",
            app_label="service_catalog",
            model="supportmessage"
        )

        self.instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.test_org)
        self.support1 = Support.objects.create(instance=self.instance1)
        self.supportmessage1 = SupportMessage.objects.create(support=self.support1, sender=self.user)
        self._test_who_has_perm_generic_without_resetting_owner_perm(permission, self.supportmessage1)

    def test_without_resetting_perms_who_has_perm_on_requestmessage_global_scope_owner_permissions(self):
        permission = Permission.objects.get_by_natural_key(
            codename="view_requestmessage",
            app_label="service_catalog",
            model="requestmessage"
        )

        self.instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.test_org, requester=self.user)
        self.request1 = Request.objects.create(instance=self.instance1, operation=self.operation)
        self.requestmessage1 = RequestMessage.objects.create(request=self.request1)
        self._test_who_has_perm_generic_without_resetting_owner_perm(permission, self.requestmessage1)

    def test_without_resetting_perms_who_has_perm_on_requestmessage_global_scope_owner_permissions2(self):
        permission = Permission.objects.get_by_natural_key(
            codename="view_requestmessage",
            app_label="service_catalog",
            model="requestmessage"
        )

        self.instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.test_org)
        self.request1 = Request.objects.create(instance=self.instance1, user=self.user, operation=self.operation)
        self.requestmessage1 = RequestMessage.objects.create(request=self.request1)
        self._test_who_has_perm_generic_without_resetting_owner_perm(permission, self.requestmessage1)

    def test_without_resetting_perms_who_has_perm_on_requestmessage_global_scope_owner_permissions3(self):
        permission = Permission.objects.get_by_natural_key(
            codename="view_requestmessage",
            app_label="service_catalog",
            model="requestmessage"
        )

        self.instance1 = Instance.objects.create(name="Instance #1", quota_scope=self.test_org)
        self.request1 = Request.objects.create(instance=self.instance1, operation=self.operation)
        self.requestmessage1 = RequestMessage.objects.create(request=self.request1, sender=self.user)
        self._test_who_has_perm_generic_without_resetting_owner_perm(permission, self.requestmessage1)
