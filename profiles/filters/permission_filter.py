from Squest.utils.squest_filter import SquestFilter
from profiles.models.squest_permission import Permission


class PermissionFilter(SquestFilter):
    class Meta:
        model = Permission
        fields = ['name', 'codename', 'content_type__model']
