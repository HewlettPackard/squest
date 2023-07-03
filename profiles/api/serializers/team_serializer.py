from profiles.api.serializers import ScopeSerializer
from profiles.models import Team, Organization


class TeamSerializer(ScopeSerializer):
    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ('id',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('organization_id'):
            self.fields.fields['org'].queryset = Organization.objects.filter(id=kwargs.get('organization_id'))