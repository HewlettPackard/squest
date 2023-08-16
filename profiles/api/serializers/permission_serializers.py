from profiles.models.squest_permission import Permission
from rest_framework.serializers import ModelSerializer

from profiles.api.serializers import ContentTypeSerializer


class PermissionSerializer(ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'
