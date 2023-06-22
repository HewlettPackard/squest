from audioop import reverse

from django.core.exceptions import ValidationError
from django.db.models import ForeignKey, PROTECT
from django.urls import reverse

from profiles.models import Organization
from profiles.models.scope import Scope


class Team(Scope):
    org = ForeignKey(
        Organization,
        blank=False,
        null=False,
        verbose_name="Organization",
        on_delete=PROTECT,
        related_name='teams',
        related_query_name='team'
    )

    def get_scopes(self):
        return self.org.get_scopes() | Scope.objects.filter(id=self.id)

    def get_absolute_url(self):
        return reverse("profiles:team_details", args=[self.pk])

    def get_perspective_users(self):
        return self.org.users

    def clean(self):
        if Team.objects.exclude(id=self.id).filter(name=self.name, org=self.org).exists():
            raise ValidationError(f"Team with this name already exist in {self.org}")

    def __str__(self):
        return f"{self.org} - {self.name}"
