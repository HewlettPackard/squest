from django.db.models import CharField, ManyToManyField, Prefetch, Q
from django.contrib.auth.models import User

from Squest.utils.squest_model import SquestModel
from profiles.models import Role
from profiles.models.rbac import RBAC


class AbstractScope(SquestModel):
    name = CharField(max_length=500)
    description = CharField(max_length=500, blank=True)

    def get_object(self):
        if hasattr(self, "scope"):
            return self.scope.get_object()
        elif hasattr(self, "globalpermission"):
            return self.globalpermission
        raise Exception("This scope is not implemented")

    @classmethod
    def get_queryset_for_user(cls, user, perm):
        qs = super().get_queryset_for_user(user, perm)
        if qs.exists():
            return qs
        app_label, codename = perm.split(".")
        qs = cls.objects.filter(
            rbac__user=user,
            rbac__role__permissions__codename=codename,
            rbac__role__permissions__content_type__app_label=app_label
        )
        return qs.distinct()

    def get_scopes(self):
        return self.get_object().get_scopes()

    def __str__(self):
        return str(self.get_object())

    @property
    def users(self):
        # get all users that are at least in one group (RBAC) of the scope.
        rbac_queryset = self.rbac.prefetch_related(
            Prefetch("role", queryset=Role.objects.all())).prefetch_related(
            Prefetch("user_set", queryset=User.objects.all()))
        return User.objects.prefetch_related(Prefetch('groups', queryset=rbac_queryset)).filter(
            groups__in=rbac_queryset).distinct()

    def get_rbac(self, role):
        rbac, _ = RBAC.objects.get_or_create(
            scope=self,
            role=role,
            defaults={'name': f'RBAC - Scope#{self.id}, Role#{role.id}'}
        )
        return rbac

    def add_user_in_role(self, user, role):
        rbac = self.get_rbac(role)
        rbac.user_set.add(user)

    def remove_user_in_role(self, user, role):
        rbac = self.get_rbac(role)
        rbac.user_set.remove(user)

    def remove_user(self, user):
        for rbac in self.rbac.filter(user=user):
            rbac.user_set.remove(user)

    def get_users_in_role(self, role):
        return self.get_rbac(role).user_set.all()

    def get_potential_users(self):
        return self.get_object().get_potential_users()

    def get_absolute_url(self):
        return self.get_object().get_absolute_url()


class Scope(AbstractScope):
    class Meta:
        permissions = [
            ("consume_quota_scope", "Can consume quota of the scope"),
        ]
        default_permissions = ('add', 'change', 'delete', 'view', 'list')

    roles = ManyToManyField(
        Role,
        blank=True,
        help_text="The roles assigned to the scope.",
        related_name="scopes",
        related_query_name="scopes",
        verbose_name="Default roles"
    )

    def __str__(self):
        return str(self.get_object())

    def get_object(self):
        if hasattr(self, "organization"):
            return self.organization
        elif hasattr(self, "team"):
            return self.team
        raise Exception("This scope is not implemented")

    @classmethod
    def get_queryset_for_user(cls, user, perm):
        qs = super().get_queryset_for_user(user, perm)
        if qs.exists():
            return qs
        from profiles.models import Team, Organization

        qs = Scope.objects.filter(
            Q(
                id__in=Team.get_queryset_for_user(user, perm)
            ) | Q(
                id__in=Organization.get_queryset_for_user(user, perm)

            )
        )
        return qs.distinct()

    @classmethod
    def get_Q(self, user, perm):

        return Q(
            rbac__user=user,
            rbac__role__permissions__codename=codename,
            rbac__role__permissions__content_type__app_label=app_label
        ) | Q(
            rbac__user=user,
            roles__permissions__codename=codename,
            roles__permissions__content_type__app_label=app_label
        )
