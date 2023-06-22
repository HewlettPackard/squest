from profiles.models import Role
from Squest.utils.squest_filter import SquestFilter


class RoleFilter(SquestFilter):
    class Meta:
        model = Role
        fields = ['name']
