from django.contrib.auth.models import User
from rest_framework.generics import CreateAPIView, DestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAdminUser

from profiles.api.serializers import ScopeCreateRBACSerializer
from profiles.models import AbstractScope, RBAC


class ScopeRBACCreate(CreateAPIView):
    serializer_class = ScopeCreateRBACSerializer
    permission_classes = [IsAdminUser]


class ScopeRBACDelete(DestroyAPIView):
    permission_classes = [IsAdminUser]

    def get_object(self):
        return get_object_or_404(RBAC, role__id=self.kwargs.get("role_id"), scope__id=self.kwargs.get("scope_id"))

    def perform_destroy(self, instance):
        scope = get_object_or_404(AbstractScope, id=self.kwargs.get("scope_id"))
        scope = scope.get_object()
        user = get_object_or_404(User, id=self.kwargs.get("user_id"))
        scope.remove_user_in_role(user, instance.role.name)
