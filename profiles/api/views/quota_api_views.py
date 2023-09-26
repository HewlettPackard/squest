from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated

from Squest.utils.squest_api_views import SquestListCreateAPIView, SquestRetrieveUpdateDestroyAPIView, \
    SquestObjectPermissions
from profiles.api.serializers.quota_serializer import QuotaSerializer
from profiles.filters.quota import QuotaFilter
from profiles.models import Quota


class SquestObjectPermissionsQuota(SquestObjectPermissions):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'PUT': ['%(app_label)s.change_%(scope)s_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(scope)s_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def get_required_object_permissions(self, method, model_cls, obj=None):
        scope = obj.scope
        if scope.is_team:
            scope_str = "team"
        elif scope.is_org:
            scope_str = "organization"
        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_name': model_cls._meta.model_name,
            'scope': scope_str
        }

        if method not in self.perms_map:
            raise MethodNotAllowed(method)

        return [perm % kwargs for perm in self.perms_map[method]]


class QuotaDetails(SquestRetrieveUpdateDestroyAPIView):
    serializer_class = QuotaSerializer
    queryset = Quota.objects.all()
    permission_classes = [IsAuthenticated, SquestObjectPermissionsQuota]



class QuotaListCreate(SquestListCreateAPIView):
    serializer_class = QuotaSerializer
    queryset = Quota.objects.all()
    filterset_class = QuotaFilter
