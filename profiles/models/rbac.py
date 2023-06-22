from django.contrib.auth.models import Group
from django.db.models import ForeignKey, CASCADE

from profiles.models.role import Role


class RBAC(Group):
    class Meta:
        unique_together = ('scope', 'role')

    role = ForeignKey(Role, null=False, on_delete=CASCADE)
    scope = ForeignKey("AbstractScope", null=False, on_delete=CASCADE, related_name="rbac",
                       related_query_name="rbac", )
