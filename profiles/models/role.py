from django.db.models import CharField, ManyToManyField

from Squest.utils.squest_model import SquestModel
from profiles.models.squest_permission import Permission


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

    def get_role_assignment_user_dict(self):
        from django.contrib.auth.models import User
        from profiles.models import AbstractScope
        rbac = self.rbac_set.prefetch_related("user_set", "scope").filter(user__id__isnull=False,
                                                                          scope__id__isnull=False).values_list(
            "user__id", "scope__id")
        user_dict_id = {x.id: x for x in User.objects.all()}
        scope_dict_id = {x.id: {"name": x.name, "url": x.get_absolute_url()} for x in AbstractScope.objects.all()}
        return [{"username": user_dict_id[user_id], "scope": scope_dict_id[scope_id]} for user_id, scope_id in rbac]

    def get_role_assignment_scope_dict(self):
        from profiles.models import AbstractScope
        return [{"scope": {"name": x.name, "url": x.get_absolute_url()}} for x in
                AbstractScope.objects.filter(id__in=self.scopes.values_list('id', flat=True))]
