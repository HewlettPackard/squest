from profiles.api.serializers import AbstractScopeSerializer
from profiles.models import GlobalPermission


class GlobalPermissionSerializer(AbstractScopeSerializer):
    class Meta:
        model = GlobalPermission
        fields = ('default_permissions', 'rbac')
