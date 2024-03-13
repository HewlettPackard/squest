from django.contrib.auth.models import User
from django.views.generic import RedirectView
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from Squest.utils.squest_api_views import SquestCreateAPIView, SquestDestroyAPIView, SquestObjectPermissions, \
    SquestRetrieveAPIView
from profiles.api.serializers import AbstractScopeCreateRBACSerializer
from profiles.models import AbstractScope, RBAC
from profiles.models import Scope


class SquestObjectPermissionsScope(SquestObjectPermissions):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    perms_map = {
        'GET': ['%(app_label)s.view_users_%(model_name)s'],
        'POST': ['%(app_label)s.add_users_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'DELETE': ['%(app_label)s.delete_users_%(model_name)s'],
    }

    def get_required_object_permissions(self, method, model_cls, obj=None):
        if obj is None:
            model_name = model_cls._meta.model_name
        else:
            model_name = obj.get_object()._meta.model_name
        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_name': model_name
        }

        if method not in self.perms_map:
            raise MethodNotAllowed(method)

        return [perm % kwargs for perm in self.perms_map[method]]


class ScopeRBACCreate(SquestCreateAPIView, SquestRetrieveAPIView):
    permission_classes = [IsAuthenticated, SquestObjectPermissionsScope]
    serializer_class = AbstractScopeCreateRBACSerializer
    queryset = AbstractScope.objects.all()
    lookup_url_kwarg = 'scope_id'

    def create(self, request, *args, **kwargs):
        # add instance in serializer
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



class ScopeRBACDelete(SquestDestroyAPIView):
    permission_classes = [IsAuthenticated, SquestObjectPermissionsScope]
    queryset = AbstractScope.objects.all()
    lookup_url_kwarg = 'scope_id'

    def perform_destroy(self, instance):
        user = get_object_or_404(User, id=self.kwargs.get("user_id"))
        rbac = get_object_or_404(RBAC, role__id=self.kwargs.get("role_id"), scope__id=self.kwargs.get("scope_id"))
        instance.remove_user_in_role(user, rbac.role)


class ScopeUserDelete(SquestDestroyAPIView):
    permission_classes = [IsAuthenticated, SquestObjectPermissionsScope]
    queryset = AbstractScope.objects.all()
    lookup_url_kwarg = 'scope_id'

    def perform_destroy(self, instance):
        user = get_object_or_404(User, id=self.kwargs.get("user_id"))
        instance.remove_user(user)


class RedirectScopeDetails(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        pk = kwargs.pop("pk")
        scope = get_object_or_404(Scope, pk=pk)
        return scope.get_url().replace('/ui/', '/api/')
