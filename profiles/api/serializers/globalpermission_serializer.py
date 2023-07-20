from rest_framework.serializers import ModelSerializer

from profiles.api.serializers import RBACSerializer
from profiles.models import GlobalPermission


class GlobalPermissionSerializer(ModelSerializer):
    rbac = RBACSerializer(many=True, read_only=True)

    class Meta:
        model = GlobalPermission
        fields = ('user_permissions', 'rbac')
