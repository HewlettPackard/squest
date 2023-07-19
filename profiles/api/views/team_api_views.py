from Squest.utils.squest_api_views import SquestRetrieveUpdateDestroyAPIView, SquestListCreateAPIView
from profiles.api.serializers import TeamSerializer
from profiles.filters import TeamFilter
from profiles.models import Team


class TeamDetails(SquestRetrieveUpdateDestroyAPIView):
    serializer_class = TeamSerializer
    queryset = Team.objects.all()


class TeamListCreate(SquestListCreateAPIView):
    serializer_class = TeamSerializer
    queryset = Team.objects.all()
    filterset_class = TeamFilter
