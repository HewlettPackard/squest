from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, CharField
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from profiles.models import Role, UserRoleBinding


class Team(Model):
    name = CharField(max_length=100,
                     blank=False,
                     unique=True)

    def __init__(self, *args, **kwargs):
        super(Team, self).__init__(*args, **kwargs)
        self.roles = Role.objects.filter(content_type=ContentType.objects.get_for_model(Team))

    def add_user_in_role(self, user, role_name):
        UserRoleBinding.objects.get_or_create(
            user=user,
            content_type=ContentType.objects.get_for_model(Team),
            object_id=self.id,
            role=self.roles.get(name=role_name)
        )
        from profiles.models import TeamRoleBinding
        for binding in TeamRoleBinding.objects.filter(team=self):
            binding.assign_permissions(user)

    def get_users_in_role(self, role_name):
        bindings = UserRoleBinding.objects.filter(role=self.roles.get(name=role_name), object_id=self.id)
        return User.objects.filter(id__in=[binding.user.id for binding in bindings])

    def get_all_users(self):
        bindings = UserRoleBinding.objects.filter(role__in=self.roles, object_id=self.id)
        return User.objects.filter(id__in=[binding.user.id for binding in bindings])

    def remove_user(self, user):
        bindings = UserRoleBinding.objects.filter(user=user,
                                                  content_type=ContentType.objects.get_for_model(Team),
                                                  object_id=self.id)
        for binding in bindings:
            binding.delete()
        from profiles.models import TeamRoleBinding
        for binding in TeamRoleBinding.objects.filter(team=self):
            binding.remove_permissions(user)

    def get_roles_of_users(self):
        roles = dict()
        for user in self.get_all_users():
            roles[user.id] = [binding.role.name for binding in UserRoleBinding.objects.filter(
                user=user,
                content_type=ContentType.objects.get_for_model(Team),
                object_id=self.id)]
        return roles

    def __str__(self):
        return self.name


@receiver(pre_delete, sender=Team)
def unset_permission(sender, instance, **kwargs):
    from profiles.models import TeamRoleBinding
    for binding in TeamRoleBinding.objects.filter(team=instance):
        binding.remove_permissions()
