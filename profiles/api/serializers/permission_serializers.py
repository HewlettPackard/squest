from rest_framework.serializers import ModelSerializer

from profiles.models.squest_permission import Permission


class PermissionSerializer(ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'
