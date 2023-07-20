from Squest.utils.squest_filter import SquestFilter
from profiles.models import Role


class RoleFilter(SquestFilter):
    class Meta:
        model = Role
        fields = ['name']
