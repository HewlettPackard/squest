from django.contrib.auth.models import Permission
from django.urls import reverse

from Squest.utils.squest_model import SquestModel


class Permission(SquestModel, Permission):
    class Meta:
        proxy = True
        default_permissions = ('add', 'change', 'delete', 'view', 'list')

    def get_permission_str(self):
        return f"{self.content_type.app_label}.{self.codename}"

    def get_absolute_url(self):
        return reverse(f"{self._meta.app_label}:{self._meta.model_name}_list")
