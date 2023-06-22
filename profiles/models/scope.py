from django.db.models import CharField, Model, ManyToManyField, Prefetch, Q, ForeignKey
from django.contrib.auth.models import User

from Squest.utils.squest_model import SquestModel
from profiles.models import Role
from profiles.models.rbac import RBAC


class AbstractScope(SquestModel):
    name = CharField(max_length=500)
    description = CharField(max_length=500, blank=True)
    roles = ManyToManyField(
        Role,
        blank=True,
        help_text="The roles assign to the scope.",
        related_name="scopes",
        related_query_name="scopes",
        verbose_name="Default roles"
    )

    def get_queryset_for_user(cls, user, perm):
        qs = super().get_queryset_for_user(user, perm)
        if qs.exists():
            return qs
        app_label, codename = perm.split(".")
        return Scope.objects.filter(rbac__user=user,
                                    rbac__role__permissions__codename=codename,
                                    rbac__role__permissions__content_type__app_label=app_label) | \
               Scope.objects.filter(Q(team__org__rbac__user=user),
                                    scope__rbac__role__permissions__codename=codename,
                                    scope__rbac__role__permissions__content_type__app_label=app_label)

    def get_scopes(self):
        if hasattr(self, "organization"):
            return self.organization.get_scopes()
        elif hasattr(self, "team"):
            return self.team.get_scopes()
        else:
            raise Exception("Not implemented")

    def __str__(self):
        if hasattr(self, "organization"):
            return str(self.organization)
        elif hasattr(self, "team"):
            return str(self.team)
        else:
            raise Exception("Not implemented")

    @property
    def users(self):
        rbac_queryset = self.rbac.prefetch_related(
            Prefetch("role", queryset=Role.objects.all())).prefetch_related(
            Prefetch("user_set", queryset=User.objects.all()))
        return User.objects.prefetch_related(Prefetch('groups', queryset=rbac_queryset)).filter(
            groups__in=rbac_queryset).distinct()

    def get_group_name_with_role(self, role):
        return f'RBAC Groups - Group#{self.id}, Role#{role.id}'

    def get_group_role(self, role_name):
        from profiles.models import Role
        role = Role.objects.get(name=role_name)
        group, _ = RBAC.objects.get_or_create(
            scope=self,
            role=role,
            defaults={'name': self.get_group_name_with_role(role)}
        )
        return group

    def add_user_in_role(self, user, role_name):
        group = self.get_group_role(role_name)
        group.user_set.add(user)

    def remove_user_in_role(self, user, role_name):
        group = self.get_group_role(role_name)
        group.user_set.remove(user)

    def remove_user(self, user):

        for rbac in self.rbac.filter(user=user):
            rbac.user_set.remove(user)

    def get_users_in_role(self, role_name):
        return self.get_group_role(role_name).user_set.all()

    def get_perspective_users(self):
        return User.objects.all()

    def get_absolute_url(self):
        if hasattr(self, "organization"):
            return self.organization.get_absolute_url()
        elif hasattr(self, "team"):
            return self.team.get_absolute_url()
        else:
            return ""


class Scope(AbstractScope):
    pass


class SquestScope(AbstractScope):
    def save(self, *args, **kwargs):
        self.pk = 1
        super(SquestScope, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1, name="Global Scope")
        return obj
