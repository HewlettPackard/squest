from django.contrib.auth.models import Permission
from Squest.utils.squest_filter import SquestFilter


class PermissionFilter(SquestFilter):
    class Meta:
        model = Permission
        fields = ['name', 'codename', 'content_type__model']
