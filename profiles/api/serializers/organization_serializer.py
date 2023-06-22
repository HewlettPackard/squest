from rest_framework.serializers import ModelSerializer

from profiles.models import Organization


class OrganizationSerializer(ModelSerializer):

    class Meta:
        model = Organization
        fields = ('name',)
