from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser

from profiles.api.serializers import TeamSerializer
from profiles.filters import TeamFilter
from profiles.models import Team


class OrganizationTeamDetails(RetrieveUpdateDestroyAPIView):
    serializer_class = TeamSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return super().get_queryset().filter(org__id=self.kwargs.get('organization_id'))


class OrganizationTeamListCreate(ListCreateAPIView):
    serializer_class = TeamSerializer
    permission_classes = [IsAdminUser]
    queryset = Team.objects.all()
    filterset_class = TeamFilter

    def get_queryset(self):
        return super().get_queryset().filter(org__id=self.kwargs.get('organization_id'))


class TeamDetails(RetrieveUpdateDestroyAPIView):
    serializer_class = TeamSerializer
    permission_classes = [IsAdminUser]
    queryset = Team.objects.all()


class TeamListCreate(ListCreateAPIView):
    serializer_class = TeamSerializer
    permission_classes = [IsAdminUser]
    queryset = Team.objects.all()
    filterset_class = TeamFilter
