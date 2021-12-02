from profiles.models.team import Team
from Squest.utils.squest_filter import SquestFilter


class TeamFilter(SquestFilter):
    class Meta:
        model = Team
        fields = ['name']
