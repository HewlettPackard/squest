from Squest.utils.squest_filter import SquestFilter
from profiles.models.team import Team


class TeamFilter(SquestFilter):
    class Meta:
        model = Team
        fields = ['name','org']
