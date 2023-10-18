from Squest.utils.squest_filter import SquestFilter
from profiles.models.squest_permission import Permission


class PermissionFilter(SquestFilter):
    class Meta:
        model = Permission
        fields = ['name', 'codename', 'content_type__model']

    def __init__(self, *args, **kwargs):
        super(PermissionFilter, self).__init__(*args, **kwargs)
        self.filters['content_type__model'].field.label = 'Model'
