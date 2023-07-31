from profiles.models.squest_permission import Permission
from django.db.models import CharField, ManyToManyField

from Squest.utils.squest_model import SquestModel


class AbstractRole(SquestModel):
    class Meta:
        abstract = True
        default_permissions = ('add', 'change', 'delete', 'view', 'list')

    name = CharField(max_length=100,
                     blank=False, unique=True)
    description = CharField(max_length=500, blank=True)
    permissions = ManyToManyField(
        Permission,
        blank=True,
        help_text="Permissions linked to this role.",
        limit_choices_to={"content_type__app_label__in": ["service_catalog", "profiles", "resource_tracker_v2", "auth"]}
    )

    def __str__(self):
        return self.name


class Role(AbstractRole):
    pass
