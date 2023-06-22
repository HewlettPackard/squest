from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import Permission

from service_catalog.models import Instance, Request, Support
from rest_framework.permissions import DjangoObjectPermissions


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


class MagicAdminBackend(BaseBackend):
    def has_perm(self, user_obj, perm, obj=None):
        # return True
        print(f"has perm called for user_obj={user_obj},perm={perm},obj={obj}")
        #
        # if obj == None:
        #     return False
        #     print(f"has perm with no answer for user_obj={user_obj},perm={perm},obj={obj}")

        if isinstance(obj, Instance):
            if obj.spoc == user_obj:
                if perm in ["service_catalog.view_instance"]:
                    return True
            scopes = obj.get_scopes()
            app_label, codename = perm.split(".")
            test_perm = Permission.objects.filter(roles__rbac__scope__in=scopes, roles__rbac__user=user_obj,
                                                  codename=codename,
                                                  content_type__app_label=app_label)
            if test_perm.exists():
                return True

        #     return False
        # elif isinstance(obj, Request):
        #     return user_obj.has_perm(perm="service_catalog.view_instance", obj=obj.instance)
        # elif isinstance(obj, Support):
        #     return user_obj.has_perm(perm=perm, obj=obj.instance)
        # else:
        #     print(f"has perm with no answer(else) for user_obj={user_obj},perm={perm},obj={obj}")
        #     return False
        # return False
