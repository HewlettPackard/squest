from rest_framework.serializers import ModelSerializer

from profiles.api.serializers import RoleSerializer
from profiles.models import RBAC


class RBACSerializer(ModelSerializer):
    role = RoleSerializer(read_only=True)

    class Meta:
        model = RBAC
        fields = ['role', 'user_set']
