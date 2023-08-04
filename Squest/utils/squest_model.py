from django.contrib.admin.utils import NestedObjects
from django.contrib.contenttypes.models import ContentType
from django.db import router
from django.db.models import Model, Q, DateTimeField
from django.urls import reverse
from django.utils.html import format_html
from django.utils.text import capfirst


class SquestDeleteCascadeMixIn(Model):
    class Meta:
        abstract = True

    exclude_object_type_list_for_delete = list()

    @staticmethod
    def format_callback(squest_object):
        try:
            link = squest_object.get_absolute_url()
        except Exception as e:
            return f'{squest_object}'
        else:
            return format_html('<a href="{}">{}</a>',
                               link,
                               squest_object)

    def get_exclude_object_type_list_for_delete(self):
        return self.exclude_object_type_list_for_delete

    def get_related_objects_cascade(self):
        using = router.db_for_write(self._meta.model)
        collector = NestedObjects(using=using)
        collector.collect([self])
        obj_list = list()
        excluded_objects = self.get_exclude_object_type_list_for_delete()
        for model in collector.model_objs:
            for squest_object in collector.model_objs[model]:
                if squest_object == self:
                    continue
                if squest_object._meta.object_name in excluded_objects:
                    continue
                obj_list.append(SquestDeleteCascadeMixIn.format_callback(squest_object))
        return obj_list


class SquestRBAC(Model):
    class Meta:
        abstract = True

    @classmethod
    def get_q_filter(cls, user, perm):
        return Q(pk=None)

    @classmethod
    def get_queryset_for_user(cls, user, perm, unique=True):
        from profiles.models.squest_permission import Permission

        # superuser
        if user.is_superuser:
            return cls.objects.distinct() if unique else cls.objects.all()
        app_label, codename = perm.split(".")
        from profiles.models import GlobalPermission
        squest_scope = GlobalPermission.load()
        # Global permission (Class based)
        if Permission.objects.filter(
                # Permissions for all user
                Q(
                    globalpermission=squest_scope,
                    codename=codename,
                    content_type__app_label=app_label
                    # Global perm groups
                ) | Q(
                    role__rbac__scope=squest_scope,
                    role__rbac__user=user,
                    codename=codename,
                    content_type__app_label=app_label
                )

        ).exists():
            return cls.objects.distinct() if unique else cls.objects.all()
        # Permission (Object based)
        qs = cls.objects.filter(cls.get_q_filter(user, perm))
        if unique:
            qs = qs.distinct()
        return qs

    def get_scopes(self):
        from profiles.models import GlobalPermission
        squest_scope = GlobalPermission.load()
        return squest_scope.get_scopes()


class SquestChangelog(Model):
    class Meta:
        abstract = True

    created = DateTimeField(
        auto_now_add=True,
        blank=True,
        null=True
    )
    last_updated = DateTimeField(
        auto_now=True,
        blank=True,
        null=True
    )


class SquestModel(SquestRBAC, SquestChangelog, SquestDeleteCascadeMixIn):
    class Meta:
        abstract = True
        default_permissions = ('add', 'change', 'delete', 'view', 'list')

    def get_content_type(self):
        return ContentType.objects.get_by_natural_key(app_label=self._meta.app_label, model=self._meta.model_name)

    def get_absolute_url(self):
        content_type = self.get_content_type()
        return reverse(f"{content_type.app_label}:{content_type.model}_details", args=[self.pk])
