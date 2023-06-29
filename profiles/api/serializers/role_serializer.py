from rest_framework.serializers import ModelSerializer

from profiles.models import Role


class RoleSerializer(ModelSerializer):

    class Meta:
        model = Role
        fields = '__all__'
