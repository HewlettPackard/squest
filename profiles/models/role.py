from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, CharField, ForeignKey, CASCADE, ManyToManyField


class Role(Model):
    class Meta:
        unique_together = ('name', 'content_type')

    name = CharField(max_length=100,
                     blank=False)
    description = CharField(max_length=500, blank=True)
    content_type = ForeignKey(ContentType, null=True, default=None, on_delete=CASCADE)
    permissions = ManyToManyField(
        Permission,
        blank=True,
        help_text="Permissions linked to this role.",
        related_name="roles",
        related_query_name="roles",
    )

    def __str__(self):
        return self.name
