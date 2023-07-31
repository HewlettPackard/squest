from profiles.models.squest_permission import Permission

from Squest.utils.squest_api_views import SquestListAPIView, SquestRetrieveAPIView
from profiles.api.serializers import PermissionSerializer
from profiles.filters import PermissionFilter


class PermissionDetails(SquestRetrieveAPIView):
    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()


class PermissionList(SquestListAPIView):
    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()
    filterset_class = PermissionFilter
