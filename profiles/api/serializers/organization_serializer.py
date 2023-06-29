from profiles.api.serializers import ScopeSerializer
from profiles.models import Organization


class OrganizationSerializer(ScopeSerializer):
    class Meta:
        model = Organization
        fields = '__all__'
        read_only_fields = ('id', 'teams')
