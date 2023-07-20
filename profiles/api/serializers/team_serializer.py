from profiles.api.serializers import ScopeSerializer
from profiles.models import Team


class TeamSerializer(ScopeSerializer):
    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ('id',)
