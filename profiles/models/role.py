from django.contrib.auth.models import Permission
from django.db.models import Model, CharField, ManyToManyField
from django.urls import reverse


class AbstractRole(Model):
    class Meta:
        abstract = True

    name = CharField(max_length=100,
                     blank=False, unique=True)
    description = CharField(max_length=500, blank=True)
    permissions = ManyToManyField(
        Permission,
        blank=True,
        help_text="Permissions linked to this role."
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("profiles:role_details", args=[self.pk])


class Role(AbstractRole):
    pass
