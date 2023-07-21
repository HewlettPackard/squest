from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q

from Squest.utils.squest_model import SquestModel
from profiles.models.scope import Scope


class Organization(Scope):
    class Meta:
        permissions = [
            ("view_users_organization", "Can view users in organization"),
            ("add_users_organization", "Can add users in organization"),
            ("delete_users_organization", "Can delete users in organization"),
        ]
        default_permissions = ('add', 'change', 'delete', 'view', 'list')

    def __str__(self):
        return self.name

    def get_scopes(self):
        from profiles.models import GlobalPermission, AbstractScope
        squest_scope = GlobalPermission.load()
        return squest_scope.get_scopes() | AbstractScope.objects.filter(id=self.id)

    def get_potential_users(self):
        return User.objects.all()

    def remove_user_in_role(self, user, role):
        super(Organization, self).remove_user_in_role(user, role)
        if user not in self.users:
            for team in self.teams.all():
                team.remove_user(user)

    def remove_user(self, user):
        super(Organization, self).remove_user(user)
        for team in self.teams.all():
            team.remove_user(user)

    def clean(self):
        if Organization.objects.exclude(id=self.id).filter(name=self.name).exists():
            raise ValidationError("Organization with this name already exist")

    def get_absolute_url(self):
        return super(SquestModel, self).get_absolute_url()

    @classmethod
    def get_q_filter(cls, user, perm):
        app_label, codename = perm.split(".")
        return Q(
                # Groups
                rbac__user=user,
                rbac__role__permissions__codename=codename,
                rbac__role__permissions__content_type__app_label=app_label
            ) | Q(
                # Default role
                rbac__user=user,
                roles__permissions__codename=codename,
                roles__permissions__content_type__app_label=app_label
            )
