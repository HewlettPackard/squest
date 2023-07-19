from django.core.exceptions import ValidationError
from django.db.models import ForeignKey, PROTECT, Q

from Squest.utils.squest_model import SquestModel
from profiles.models import Organization
from profiles.models.scope import Scope


class Team(Scope):
    class Meta:
        permissions = [
            ("view_users_team", "Can view users in team"),
            ("add_users_team", "Can add users in team"),
            ("delete_users_team", "Can delete users in team"),
        ]
        default_permissions = ('add', 'change', 'delete', 'view', 'list')

    org = ForeignKey(
        Organization,
        blank=False,
        null=False,
        verbose_name="Organization",
        on_delete=PROTECT,
        related_name='teams',
        related_query_name='team'
    )

    def get_absolute_url(self):
        return super(SquestModel, self).get_absolute_url()

    @classmethod
    def get_queryset_for_user(cls, user, perm):
        qs = super(SquestModel, cls).get_queryset_for_user(user, perm)
        if qs.exists():
            return qs
        app_label, codename = perm.split(".")
        qs = cls.objects.filter(
            Q(
                # Organization role
                org__rbac__user=user,
                org__rbac__role__permissions__codename=codename,
                org__rbac__role__permissions__content_type__app_label=app_label
            ) | Q(
                # Organization default_role
                org__rbac__user=user,
                org__roles__permissions__codename=codename,
                org__roles__permissions__content_type__app_label=app_label
            ) | Q(
                # Team role
                rbac__user=user,
                rbac__role__permissions__codename=codename,
                rbac__role__permissions__content_type__app_label=app_label
            ) | Q(
                # Team default roles
                rbac__user=user,
                roles__permissions__codename=codename,
                roles__permissions__content_type__app_label=app_label
            )
        )
        return qs.distinct()

    def get_scopes(self):
        from profiles.models.scope import AbstractScope
        return self.org.get_scopes() | AbstractScope.objects.filter(id=self.id)

    def get_potential_users(self):
        return self.org.users

    def add_user_in_role(self, user, role):
        if user not in self.get_potential_users():
            raise ValidationError(
                f"The User {user}(#{user.id}) must be in the Organization {self.org}(#{self.org.id} to be added in the Team")
        super(Team, self).add_user_in_role(user, role)

    def clean(self):
        if Team.objects.exclude(id=self.id).filter(name=self.name, org=self.org).exists():
            raise ValidationError(f"Team with this name already exist in {self.org}")

    def __str__(self):
        return f"{self.org} - {self.name}"
