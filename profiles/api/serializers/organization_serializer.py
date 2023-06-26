from rest_framework.serializers import ModelSerializer

from profiles.models import Organization


class OrganizationSerializer(ModelSerializer):

    class Meta:
        model = Organization
        fields = '__all__'
        read_only_fields = ('id',)
