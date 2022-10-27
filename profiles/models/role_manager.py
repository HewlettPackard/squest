from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from django.dispatch import receiver

from profiles.models.role import Role
from profiles.models.user_role_binding import UserRoleBinding
from service_catalog.models.request import pre_delete


class RoleManager(Model):
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.roles = Role.objects.filter(content_type=ContentType.objects.get_for_model(type(self)))

    def add_user_in_role(self, user, role_name):
        UserRoleBinding.objects.get_or_create(
            user=user,
            content_type=ContentType.objects.get_for_model(type(self)),
            object_id=self.id,
            role=self.roles.get(name=role_name)
        )

    def get_users_in_role(self, role_name):
        bindings = UserRoleBinding.objects.filter(role=self.roles.get(name=role_name), object_id=self.id)
        return User.objects.filter(id__in=[binding.user.id for binding in bindings])

    def get_all_users(self):
        bindings = UserRoleBinding.objects.filter(role__in=self.roles, object_id=self.id)
        return User.objects.filter(id__in=[binding.user.id for binding in bindings])

    def get_roles_of_users(self):
        roles = dict()
        for user in self.get_all_users():
            roles[user.id] = [binding.role.name for binding in UserRoleBinding.objects.filter(
                user=user,
                content_type=ContentType.objects.get_for_model(type(self)),
                object_id=self.id)]
        return roles

    def remove_user_in_role(self, user, role_name=None):
        if role_name:
            bindings = UserRoleBinding.objects.filter(user=user,
                                                      content_type=ContentType.objects.get_for_model(type(self)),
                                                      object_id=self.id, role__name=role_name)
        else:
            bindings = UserRoleBinding.objects.filter(user=user,
                                                      content_type=ContentType.objects.get_for_model(type(self)),
                                                      object_id=self.id)
        for binding in bindings:
            binding.delete()

    def add_team_in_role(self, team, role_name):
        from profiles.models import TeamRoleBinding
        TeamRoleBinding.objects.get_or_create(
            team=team,
            content_type=ContentType.objects.get_for_model(type(self)),
            object_id=self.id,
            role=self.roles.get(name=role_name)
        )

    def get_teams_in_role(self, role_name):
        from profiles.models import TeamRoleBinding, Team
        bindings = TeamRoleBinding.objects.filter(role=self.roles.get(name=role_name), object_id=self.id)
        return Team.objects.filter(id__in=[binding.team.id for binding in bindings])

    def get_all_teams(self):
        from profiles.models import TeamRoleBinding, Team
        bindings = TeamRoleBinding.objects.filter(role__in=self.roles, object_id=self.id)
        return Team.objects.filter(id__in=[binding.team.id for binding in bindings])

    def get_roles_of_teams(self):
        from profiles.models import TeamRoleBinding
        roles = dict()
        for team in self.get_all_teams():
            roles[team.id] = [binding.role.name for binding in TeamRoleBinding.objects.filter(
                team=team,
                content_type=ContentType.objects.get_for_model(type(self)),
                object_id=self.id)]
        return roles

    def remove_team_in_role(self, team, role_name=None):
        from profiles.models import TeamRoleBinding
        if role_name:
            bindings = TeamRoleBinding.objects.filter(team=team,
                                                      content_type=ContentType.objects.get_for_model(type(self)),
                                                      object_id=self.id, role__name=role_name)
        else:
            bindings = TeamRoleBinding.objects.filter(team=team,
                                                      content_type=ContentType.objects.get_for_model(type(self)),
                                                      object_id=self.id)
        for binding in bindings:
            binding.delete()

    def remove_all_bindings(self):
        from profiles.models import TeamRoleBinding
        for binding in TeamRoleBinding.objects.filter(role__in=self.roles, object_id=self.id):
            binding.remove_permissions()
        TeamRoleBinding.objects.filter(role__in=self.roles, object_id=self.id).delete()
        for binding in UserRoleBinding.objects.filter(role__in=self.roles, object_id=self.id):
            binding.remove_permissions()
        UserRoleBinding.objects.filter(role__in=self.roles, object_id=self.id).delete()


@receiver(pre_delete)
def remove_all_binding(sender, instance, **kwargs):
    from profiles.models import Team
    if isinstance(instance, Team):
        from profiles.models import TeamRoleBinding
        for binding in TeamRoleBinding.objects.filter(team=instance):
            binding.remove_permissions()
    if issubclass(sender, RoleManager):
        instance.remove_all_bindings()
