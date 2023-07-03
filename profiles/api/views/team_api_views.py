from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser

from profiles.api.serializers import TeamSerializer
from profiles.filters import TeamFilter
from profiles.models import Team


class TeamDetails(RetrieveUpdateDestroyAPIView):
    serializer_class = TeamSerializer
    permission_classes = [IsAdminUser]
    queryset = Team.objects.all()


class TeamListCreate(ListCreateAPIView):
    serializer_class = TeamSerializer
    permission_classes = [IsAdminUser]
    queryset = Team.objects.all()
    filterset_class = TeamFilter
