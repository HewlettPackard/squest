from django.contrib.auth.models import Permission
from django.urls import reverse

from Squest.utils.squest_model import SquestRBAC, SquestDeleteCascadeMixIn


class Permission(SquestRBAC, Permission, SquestDeleteCascadeMixIn):
    class Meta:
        proxy = True
        default_permissions = ('add', 'change', 'delete', 'view', 'list')
        ordering = ["content_type__model", "codename"]

    @property
    def permission_str(self):
        return f"{self.content_type.app_label}.{self.codename}"

    def get_absolute_url(self):
        return reverse(f"profiles:permission_list")

    def __str__(self):
        return self.codename
