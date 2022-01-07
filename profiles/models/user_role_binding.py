from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, ForeignKey, CASCADE, PositiveIntegerField
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from guardian.models import UserObjectPermission

from profiles.models.role import Role


class UserRoleBinding(Model):
    class Meta:
        unique_together = ('user', 'content_type', 'object_id', 'role')

    role = ForeignKey(Role, null=False, on_delete=CASCADE)
    user = ForeignKey(User, null=False, on_delete=CASCADE)
    content_type = ForeignKey(ContentType, null=False, on_delete=CASCADE)
    object_id = PositiveIntegerField(null=False)
    content_object = GenericForeignKey('content_type', 'object_id')

    def get_object(self):
        return self.content_type.get_object_for_this_type(id=self.object_id)

    def assign_permissions(self):
        for permission in self.role.permissions.all():
            UserObjectPermission.objects.assign_perm(permission.codename, self.user, obj=self.get_object())

    def remove_permissions(self):
        from profiles.models import Team, TeamRoleBinding
        user_bindings = UserRoleBinding.objects.filter(user=self.user, content_type=self.content_type, object_id=self.object_id)
        teams = [Team.objects.get(id=binding.object_id) for binding in
                 UserRoleBinding.objects.filter(user=self.user, content_type=ContentType.objects.get_for_model(Team))]
        team_bindings = TeamRoleBinding.objects.filter(team__in=teams, content_type=self.content_type, object_id=self.object_id)
        others_permission = list()
        for binding in user_bindings:
            others_permission = [*others_permission, *list(binding.role.permissions.all())]
        for binding in team_bindings:
            others_permission = [*others_permission, *list(binding.role.permissions.all())]
        for permission in self.role.permissions.all():
            if permission not in others_permission:
                UserObjectPermission.objects.remove_perm(permission.codename, self.user, obj=self.get_object())


@receiver(post_save, sender=UserRoleBinding)
def set_permission(sender, instance, created, **kwargs):
    if created:
        instance.assign_permissions()


@receiver(post_delete, sender=UserRoleBinding)
def unset_permission(sender, instance, **kwargs):
    instance.remove_permissions()
