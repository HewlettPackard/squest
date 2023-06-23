from django.contrib.auth.models import Permission
from django.db.models import Model



class SquestRBAC(Model):
    class Meta:
        abstract = True

    @classmethod
    def get_queryset_for_user(cls, user, perm):
        if user.is_superuser:
            return cls.objects.all()

        app_label, codename = perm.split(".")

        from profiles.models.scope import GlobalPermission
        squest_scope = GlobalPermission.load()
        if Permission.objects.filter(
                role__rbac__scope=squest_scope,
                role__rbac__user=user,
                codename=codename,
                content_type__app_label=app_label
        ).exists():
            return cls.objects.all()
        return cls.objects.none()


    def get_scopes(self):
        pass


class SquestChangelog(Model):
    class Meta:
        abstract = True


class SquestModel(SquestRBAC, SquestChangelog):
    class Meta:
        abstract = True
