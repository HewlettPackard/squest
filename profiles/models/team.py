from django.db.models import CharField
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from profiles.models.role_manager import RoleManager


class Team(RoleManager):
    name = CharField(max_length=100,
                     blank=False,
                     unique=True)

    def add_user_in_role(self, user, role_name):
        super(Team, self).add_user_in_role(user, role_name)
        from profiles.models import TeamRoleBinding
        for binding in TeamRoleBinding.objects.filter(team=self):
            binding.assign_permissions(user)

    def remove_user_in_role(self, user, role_name=None):
        super(Team, self).remove_user_in_role(user, role_name)
        from profiles.models import TeamRoleBinding
        if user not in self.get_all_users():
            for binding in TeamRoleBinding.objects.filter(team=self):
                binding.remove_permissions(user)

    def __str__(self):
        return self.name
