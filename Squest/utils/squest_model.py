from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, Q
from django.urls import reverse


class SquestRBAC(Model):
    class Meta:
        abstract = True

    def get_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse(f"{content_type.app_label}:{content_type.model}_details", args=[self.pk])

    @classmethod
    def get_queryset_for_user(cls, user, perm):
        if user.is_superuser:
            return cls.objects.distinct()

        app_label, codename = perm.split(".")

        from profiles.models import GlobalPermission
        squest_scope = GlobalPermission.load()
        if Permission.objects.filter(
                # Permissions for all user
                Q(globalpermission=squest_scope,
                  codename=codename,
                  content_type__app_label=app_label) |
                # Global perm groups
                Q(role__rbac__scope=squest_scope,
                  role__rbac__user=user,
                  codename=codename,
                  content_type__app_label=app_label)
        ).exists():
            return cls.objects.distinct()
        return cls.objects.none()

    def get_scopes(self):
        from profiles.models import GlobalPermission
        squest_scope = GlobalPermission.load()
        return squest_scope.get_scopes()


class SquestChangelog(Model):
    class Meta:
        abstract = True


class SquestModel(SquestRBAC, SquestChangelog):
    class Meta:
        abstract = True
        default_permissions = ('add', 'change', 'delete', 'view', 'list')
