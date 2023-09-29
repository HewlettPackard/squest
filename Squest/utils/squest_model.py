from django.contrib.admin.utils import NestedObjects
from django.contrib.contenttypes.models import ContentType
from django.db import router
from django.db.models import Model, Q, DateTimeField
from django.urls import reverse
from django.utils.html import format_html


class SquestDeleteCascadeMixIn(Model):
    class Meta:
        abstract = True

    class_displayed_in_cascade = ["Request",
                                  "Instance",
                                  "Support",
                                  "Operation",
                                  "JobTemplate",
                                  "TowerServer",
                                  "Resource",
                                  "ResourceGroup",
                                  "Organization",
                                  "Team",
                                  "ApprovalWorkflow",
                                  "ApprovalStep",
                                  ]

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

    def get_class_displayed_in_cascade(self):
        # Remove current class from displayed objects
        class_name = self._meta.object_name
        if class_name == "AbstractScope":
            class_name = self.get_object()._meta.object_name
        try:
            self.class_displayed_in_cascade.remove(class_name)
        except ValueError:
            pass
        return self.class_displayed_in_cascade

    def get_related_objects_cascade(self):
        using = router.db_for_write(self._meta.model)
        collector = NestedObjects(using=using)
        collector.collect([self])
        class_displayed_in_cascade = self.get_class_displayed_in_cascade()
        model_list = list()
        for model in collector.model_objs:
            obj_list = list()
            for squest_object in collector.model_objs[model]:
                if squest_object == self:
                    continue
                if squest_object._meta.object_name in class_displayed_in_cascade:
                    obj_list.append(SquestDeleteCascadeMixIn.format_callback(squest_object))
            if obj_list:
                model_list.append(model._meta.object_name)
                model_list.append(obj_list)
        return model_list


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
        from profiles.models import GlobalScope
        squest_scope = GlobalScope.load()
        # Global scope (Class based)
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
        from profiles.models import GlobalScope
        squest_scope = GlobalScope.load()
        return squest_scope.get_scopes()


    def who_has_perm(self, permission_str):
        app_label, codename = permission_str.split(".")

        # Global Perm permission for all users
        from django.contrib.auth.models import User
        from profiles.models import GlobalScope, Scope, RBAC
        if GlobalScope.load().global_permissions.filter(codename=codename,content_type__app_label=app_label).exists():
            return User.objects.all()

        scopes = self.get_scopes()
        ## Default role scopes
        ### Team and Org in get_scopes that have the permissions in default roles
        default_role_scopes = Scope.objects.filter(roles__permissions__content_type__app_label=app_label,roles__permissions__codename=codename, id__in=scopes)
        ### All users in RBAC related to these scopes
        rbac0 = RBAC.objects.filter(scope__in=default_role_scopes)

        ## Permission given via RBAC
        rbac1 = RBAC.objects.filter(
            Q(role__permissions__content_type__app_label=app_label,role__permissions__codename=codename, scope__in=scopes)
        )

        rbacs = rbac0 | rbac1
        return User.objects.filter(Q(groups__in=rbacs) | Q(is_superuser=True)).distinct()

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

    def is_owner(self, user):
        return False
