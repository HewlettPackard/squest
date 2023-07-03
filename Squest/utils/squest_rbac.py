import logging

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Permission

from rest_framework.permissions import DjangoObjectPermissions
logger = logging.getLogger(__name__)


class SquestPermissionRequiredMixin(PermissionRequiredMixin):
    def has_permission(self):
        return self.request.user.has_perm(self.permission_required, self.get_object())


class SquestObjectPermissions(DjangoObjectPermissions):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def has_permission(self, request, view):
        # Skip Class based permissions, otherwise we need to assign user permissions to all ours users.
        return True


class SquestRBACBackend(BaseBackend):
    def has_perm(self, user_obj, perm, obj=None):
        if obj is None:
            logger.debug(f"has perm called for user_obj={user_obj},perm={perm} with None object")
            return
        logger.debug(f"has perm called for user_obj={user_obj},perm={perm},obj={obj},type={obj._meta.label}")
        try:
            scopes = obj.get_scopes()
            app_label, codename = perm.split(".")
            test_perm = Permission.objects.filter(role__rbac__scope__in=scopes, role__rbac__user=user_obj,
                                                  codename=codename,
                                                  content_type__app_label=app_label)
            if test_perm.exists():
                logger.debug("permission granted")
                return True
        except NotImplemented:
            logger.debug("get_scopes method is not implemented for this object")
            return
