from audioop import reverse

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from profiles.models.scope import Scope


class Organization(Scope):

    def __str__(self):
        return self.name

    def get_scopes(self):
        from profiles.models.scope import SquestScope
        from profiles.models.scope import Scope
        squest_scope = SquestScope.load()
        return Scope.objects.filter(id=squest_scope.id) | Scope.objects.filter(id=self.id)

    def get_perspective_users(self):
        return User.objects.all()

    def get_name_by_role_name(self, role_name):
        return f"{self.name} - {role_name}"

    def get_absolute_url(self):
        return reverse("profiles:organization_details", args=[self.pk])

    def remove_user_in_role(self, user, role_name):
        super(Organization, self).remove_user_in_role(user, role_name)
        if user not in self.users:
            for team in self.teams.all():
                team.remove_user(user)

    def remove_user(self, user):
        super(Organization, self).remove_user_in_role(user)
        for team in self.teams.all():
            team.remove_user(user)

    def clean(self):
        if Organization.objects.exclude(id=self.id).filter(name=self.name).exists():
            raise ValidationError("Organization with this name already exist")
