from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from profiles.models import TeamRoleBinding, Role, Team, UserRoleBinding
from service_catalog.models import Instance
from tests.test_profile.test_group.test_group_base import TestGroupBase


class TestTeamRoleBinding(TestGroupBase):

    def setUp(self):
        super(TestTeamRoleBinding, self).setUp()
        self.instance = Instance.objects.create(service=None, name="Test", billing_group=None, requester=self.standard_user)
        self.instance_content_type = ContentType.objects.get_for_model(Instance)
        self.role = Role.objects.create(
            name="Test",
            description="Used for the testing",
            content_type=self.instance_content_type
        )
        self.role.permissions.add(Permission.objects.get(codename="view_instance"))
        self.binding = TeamRoleBinding.objects.create(team=self.test_team,
                                                      role=self.role,
                                                      content_type=self.instance_content_type,
                                                      object_id=self.instance.id)

    def test_on_team_delete_unset_permissions_and_remove_user_role_bindings(self):
        binding_id = self.binding.id
        user = self.test_team.get_all_users().first()
        team_content_type = ContentType.objects.get_for_model(Team)
        team_id = self.test_team.id
        self.assertTrue(user.has_perm("view_instance", self.instance))
        self.assertEqual(
            UserRoleBinding.objects.filter(content_type=team_content_type, object_id=team_id).count(),
            4
        )
        self.test_team.delete()
        self.assertFalse(TeamRoleBinding.objects.filter(id=binding_id).exists())
        self.assertFalse(user.has_perm("view_instance", self.instance))
        self.assertEqual(
            UserRoleBinding.objects.filter(content_type=team_content_type, object_id=team_id).count(),
            0
        )
