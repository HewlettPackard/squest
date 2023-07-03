from copy import copy

from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAdminUser

from profiles.api.serializers import TeamSerializer
from profiles.filters import TeamFilter
from profiles.models import Team, Organization


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

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        kwargs.setdefault('organization_id', self.kwargs['organization_id'])
        return serializer_class(*args, **kwargs)

    def create(self, request, **kwargs):
        organization = get_object_or_404(Organization, pk=self.kwargs['organization_id'])
        data = copy(request.data)
        data["org"] = organization.id
        serializer = TeamSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)


class TeamDetails(RetrieveUpdateDestroyAPIView):
    serializer_class = TeamSerializer
    permission_classes = [IsAdminUser]
    queryset = Team.objects.all()


class TeamListCreate(ListCreateAPIView):
    serializer_class = TeamSerializer
    permission_classes = [IsAdminUser]
    queryset = Team.objects.all()
    filterset_class = TeamFilter
