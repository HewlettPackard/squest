from Squest.utils.squest_api_views import SquestListCreateAPIView, SquestRetrieveUpdateDestroyAPIView
from profiles.api.serializers import RoleSerializer
from profiles.filters import RoleFilter
from profiles.models import Role


class RoleDetails(SquestRetrieveUpdateDestroyAPIView):
    serializer_class = RoleSerializer
    queryset = Role.objects.all()


class RoleListCreate(SquestListCreateAPIView):
    serializer_class = RoleSerializer
    queryset = Role.objects.all()
    filterset_class = RoleFilter
