from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, ForeignKey, CASCADE, PositiveIntegerField
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from guardian.models import UserObjectPermission

from profiles.models import Role, Team, UserRoleBinding


class TeamRoleBinding(Model):
    class Meta:
        unique_together = ('team', 'content_type', 'object_id', 'role')

    role = ForeignKey(Role, null=False, on_delete=CASCADE)
    team = ForeignKey(Team, null=False, on_delete=CASCADE)
    content_type = ForeignKey(ContentType, null=False, on_delete=CASCADE)
    object_id = PositiveIntegerField(null=False)
    content_object = GenericForeignKey('content_type', 'object_id')

    @property
    def object_type(self):
        return self.content_type.name

    @property
    def object_name(self):
        return self.content_object.__str__()

    def get_object(self):
        return self.content_type.get_object_for_this_type(id=self.object_id)

    def assign_permissions(self, user=None):
        if user:
            self._set_permission_for_user(user)
        else:
            for user in self.team.get_all_users():
                self._set_permission_for_user(user)

    def _set_permission_for_user(self, user):
        for permission in self.role.permissions.all():
            UserObjectPermission.objects.assign_perm(permission, user, obj=self.get_object())

    def remove_permissions(self, user=None):
        if user:
            self._unset_permission_for_user(user)
        else:
            for user in self.team.get_all_users():
                self._unset_permission_for_user(user)

    def _unset_permission_for_user(self, user):
        all_user_bindings = UserRoleBinding.objects.filter(user=user, content_type=self.content_type,
                                                           object_id=self.object_id)
        teams = [Team.objects.get(id=binding.object_id) for binding in
                 UserRoleBinding.objects.filter(user=user,
                                                content_type=ContentType.objects.get_for_model(Team))]
        all_team_bindings = TeamRoleBinding.objects.filter(team__in=teams, content_type=self.content_type,
                                                           object_id=self.object_id).exclude(id=self.id)
        others_permission = list()
        for binding in all_user_bindings:
            others_permission = [*others_permission, *list(binding.role.permissions.all())]
        for binding in all_team_bindings:
            others_permission = [*others_permission, *list(binding.role.permissions.all())]
        user_bindings = UserRoleBinding.objects.filter(
            user=user,
            role=self.role,
            content_type=self.content_type,
            object_id=self.object_id
        )
        if user_bindings.count() == 0:
            for permission in self.role.permissions.all():
                if permission not in others_permission:
                    UserObjectPermission.objects.remove_perm(permission, user, obj=self.get_object())


@receiver(post_save, sender=TeamRoleBinding)
def set_permission(sender, instance, created, **kwargs):
    if created:
        instance.assign_permissions()


@receiver(post_delete, sender=UserRoleBinding)
def unset_permission(sender, instance, **kwargs):
    instance.remove_permissions()
