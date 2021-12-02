from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from profiles.models import TeamRoleBinding, Role
from service_catalog.models import Instance
from tests.test_profile.test_group.test_group_base import TestGroupBase


class TestTeamRoleBinding(TestGroupBase):

    def setUp(self):
        super(TestTeamRoleBinding, self).setUp()

    def test_on_team_delete_unset_permissions(self):
        instance = Instance.objects.create(service=None, name="Test", billing_group=None, spoc=self.standard_user)
        instance_content_type = ContentType.objects.get_for_model(Instance)
        role = Role.objects.create(
            name="Test",
            description="Used for the testing",
            content_type=instance_content_type
        )
        role.permissions.add(Permission.objects.get(codename="view_instance"))
        binding = TeamRoleBinding.objects.create(team=self.test_team, role=role, content_type=instance_content_type,
                                                 object_id=instance.id)
        binding_id = binding.id
        user = self.test_team.get_all_users().first()
        self.assertTrue(user.has_perm("view_instance", instance))
        self.test_team.delete()
        self.assertFalse(TeamRoleBinding.objects.filter(id=binding_id).exists())
        self.assertFalse(user.has_perm("view_instance", instance))

