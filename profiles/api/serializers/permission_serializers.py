from django.contrib.auth.models import Permission
from rest_framework.serializers import ModelSerializer

from profiles.api.serializers import ContentTypeSerializer


class PermissionSerializer(ModelSerializer):
    content_type = ContentTypeSerializer()
    class Meta:
        model = Permission
        fields = '__all__'
