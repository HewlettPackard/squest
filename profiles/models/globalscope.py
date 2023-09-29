from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import ManyToManyField
from django.urls import reverse

from profiles.models import AbstractScope
from profiles.models.squest_permission import Permission


class GlobalScope(AbstractScope):
    class Meta:
        permissions = [
            ("view_users_globalscope", "Can view users in global scope"),
            ("add_users_globalscope", "Can add users in global scope"),
            ("delete_users_globalscope", "Can delete users in global scope"),
        ]
        default_permissions = ('add', 'change', 'delete', 'view', 'list')

    global_permissions = ManyToManyField(
        Permission,
        blank=True,
        help_text="Permissions assigned to all users without exception.",
        limit_choices_to={"content_type__app_label__in": ["service_catalog", "profiles", "resource_tracker_v2", "auth"]},
        related_name="globalpermission",
        related_query_name="globalpermission"
    )

    owner_permissions = ManyToManyField(
        Permission,
        blank=True,
        help_text="Permissions assigned to the owner of Squest objects.",
        limit_choices_to={
            "content_type__model__in": ["instance", "request", "support", "supportmessage", "requestmessage","approvalstep"]},
        related_name="ownerpermission",
        related_query_name="ownerpermission"
    )


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(GlobalScope, self).save(*args, **kwargs)
        self.set_cache()

    def set_cache(self):
        cache.set(self.__class__.__name__, self)

    def get_absolute_url(self):
        return reverse("profiles:globalscope_rbac")

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        if cache.get(cls.__name__) is None:
            obj, created = GlobalScope.objects.get_or_create(name="GlobalScope")
            if not created:
                obj.set_cache()
            return obj
        return cache.get(cls.__name__)

    def get_potential_users(self):
        return User.objects.all()

    def get_scopes(self):
        return AbstractScope.objects.filter(id=self.id)
