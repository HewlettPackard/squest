import logging
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Permission
from django.db.models import Q
from django.utils.safestring import mark_safe

from profiles.models import GlobalPermission

logger = logging.getLogger(__name__)

from django.core.cache import cache


class SquestPermissionRequiredMixin(PermissionRequiredMixin):
    def has_permission(self):
        try:
            obj = self.get_object()
        except AttributeError:
            obj = None
        return self.request.user.has_perm(self.get_permission_required(), obj)

    def get_permission_denied_message(self):
        return mark_safe(f"Permission <b>{self.get_permission_required()}</b> required")

class SquestRBACBackend(BaseBackend):
    def has_perm(self, user_obj, perm, obj=None):

        if not user_obj.is_authenticated:
            return False

        app_label, codename = perm.split(".")

        if obj is None:
            key = f"{user_obj.id}_{perm}"
        else:
            key = f"{user_obj.id}_{perm}_{obj._meta.label}_{obj.id}"

        cached_value = cache.get(key)
        if cached_value is not None:
            logger.debug(
                f"Handled by cache: has perm called for user_obj={user_obj},perm={perm},obj={obj},type={obj._meta.label if obj else None}")
            return cached_value
        logger.debug(
            f"has perm called for user_obj={user_obj},perm={perm},obj={obj},type={obj._meta.label if obj else None}")
        if obj is None:
            scope = GlobalPermission.load()
            permission_granted = Permission.objects.filter(Q(globalpermission=scope,

                                                             codename=codename,
                                                             content_type__app_label=app_label) |

                                                           Q(role__rbac__scope=scope,
                                                             role__rbac__user=user_obj,

                                                             codename=codename,
                                                             content_type__app_label=app_label)
                                                           ).exists()
        else:
            try:
                scopes = obj.get_scopes()
            except AttributeError:
                logger.debug("get_scopes method not found")
                return user_obj.has_perm(perm) # If get_scopes not implement, call has_perm with obj=None
            permission_granted = Permission.objects.filter(Q(globalpermission__in=scopes,

                                                             codename=codename,
                                                             content_type__app_label=app_label) |

                                                           Q(role__rbac__scope__in=scopes,
                                                             role__rbac__user=user_obj,

                                                             codename=codename,
                                                             content_type__app_label=app_label) |

                                                           Q(role__scopes__in=scopes,
                                                             role__scopes__rbac__user=user_obj,

                                                             codename=codename,
                                                             content_type__app_label=app_label)
                                                           ).exists()
        cache.set(key, permission_granted, 60)
        return permission_granted
