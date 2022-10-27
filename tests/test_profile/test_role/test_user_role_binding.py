from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from profiles.models import Role, UserRoleBinding
from service_catalog.models import Instance, Request
from tests.test_profile.test_group.test_group_base import TestGroupBase
from django.db.models.signals import pre_delete


class TestUserRoleBinding(TestGroupBase):

    def setUp(self):
        super(TestUserRoleBinding, self).setUp()
        self.instance = Instance.objects.create(service=None, name="Test", billing_group=None, spoc=self.standard_user)
        self.request = Request.objects.create(fill_in_survey={}, instance=self.instance,
                                              operation=self.create_operation_test, user=self.standard_user_2)
        self.instance_content_type = ContentType.objects.get_for_model(Instance)
        self.request_content_type = ContentType.objects.get_for_model(Request)
        self.instance_role = Role.objects.create(
            name="Test",
            description="Used for the testing",
            content_type=self.instance_content_type
        )
        self.request_role = Role.objects.create(
            name="Test",
            description="Used for the testing",
            content_type=self.request_content_type
        )
        self.instance_role.permissions.add(Permission.objects.get(codename="view_instance"))
        self.request_role.permissions.add(Permission.objects.get(codename="view_request"))
        self.instance_binding = UserRoleBinding.objects.create(user=self.standard_user_2,
                                                               role=self.instance_role,
                                                               content_type=self.instance_content_type,
                                                               object_id=self.instance.id)
        self.request_binding = UserRoleBinding.objects.create(user=self.standard_user_2,
                                                              role=self.request_role,
                                                              content_type=self.request_content_type,
                                                              object_id=self.request.id)

    def test_delete_user_binding_on_instance_delete(self):
        instance_binding_id = self.instance_binding.id
        request_binding_id = self.request_binding.id
        self.instance.delete()
        self.assertFalse(UserRoleBinding.objects.filter(id=instance_binding_id).exists())
        self.assertFalse(UserRoleBinding.objects.filter(id=request_binding_id).exists())

    def test_delete_user_binding_on_request_delete(self):
        request_binding_id = self.request_binding.id
        self.request.delete()
        self.assertFalse(UserRoleBinding.objects.filter(id=request_binding_id).exists())

    def test_can_delete_user_binding_linked_to_deleted_object(self):
        old_receivers = pre_delete.receivers
        pre_delete.receivers = []
        binding_id = self.instance_binding.id
        self.instance.delete()
        self.instance_binding.delete()
        self.assertFalse(UserRoleBinding.objects.filter(id=binding_id).exists())
        pre_delete.receivers = old_receivers
