from rest_framework.serializers import ModelSerializer

from profiles.models import GlobalPermission


class GlobalPermissionSerializer(ModelSerializer):

    class Meta:
        model = GlobalPermission
        fields = ('roles',)
