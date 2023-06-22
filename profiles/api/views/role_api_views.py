from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser

from profiles.api.serializers import RoleSerializer
from profiles.filters import RoleFilter
from profiles.models import Role


class RoleDetails(RetrieveUpdateDestroyAPIView):
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]
    queryset = Role.objects.all()


class RoleListCreate(ListCreateAPIView):
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]
    queryset = Role.objects.all()
    filterset_class = RoleFilter
