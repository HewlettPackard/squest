from django.contrib.auth.models import User
from django.views.generic import RedirectView
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.reverse import reverse

from Squest.utils.squest_api_views import SquestCreateAPIView, SquestDestroyAPIView
from profiles.api.serializers import ScopeCreateRBACSerializer
from profiles.models import AbstractScope, RBAC, Organization, Scope, Team


class ScopeRBACCreate(SquestCreateAPIView):
    serializer_class = ScopeCreateRBACSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        kwargs.setdefault('scope_id', self.kwargs['scope_id'])
        return serializer_class(*args, **kwargs)


class ScopeRBACDelete(SquestDestroyAPIView):

    def get_object(self):
        return get_object_or_404(RBAC, role__id=self.kwargs.get("role_id"), scope__id=self.kwargs.get("scope_id"))

    def perform_destroy(self, instance):
        scope = get_object_or_404(AbstractScope, id=self.kwargs.get("scope_id"))
        scope = scope.get_object()
        user = get_object_or_404(User, id=self.kwargs.get("user_id"))
        scope.remove_user_in_role(user, instance.role.name)


class RedirectScopeDetails(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        pk = kwargs.pop("pk")
        scope = get_object_or_404(Scope, pk=pk)
        if scope.is_org:
            return reverse("api_organization_details", kwargs={'pk': pk})
        elif scope.is_team:
            return reverse("api_team_details", kwargs={'pk': pk})
        raise NotFound
