from profiles.models.squest_permission import Permission

from Squest.utils.squest_api_views import SquestRetrieveUpdateDestroyAPIView, SquestListCreateAPIView
from profiles.api.serializers import PermissionSerializer
from profiles.filters import PermissionFilter


class PermissionDetails(SquestRetrieveUpdateDestroyAPIView):
    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()


class PermissionListCreate(SquestListCreateAPIView):
    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()
    filterset_class = PermissionFilter
