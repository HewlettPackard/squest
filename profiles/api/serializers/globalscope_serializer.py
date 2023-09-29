from profiles.api.serializers import AbstractScopeSerializer
from profiles.models import GlobalScope


class GlobalScopeSerializer(AbstractScopeSerializer):
    class Meta:
        model = GlobalScope
        fields = ('global_permissions', 'owner_permissions', 'rbac')
