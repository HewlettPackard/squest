from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import ManyToManyField
from django.urls import reverse

from profiles.models import AbstractScope
from profiles.models.squest_permission import Permission


class GlobalPermission(AbstractScope):
    class Meta:
        permissions = [
            ("view_users_globalpermission", "Can view users in global permission"),
            ("add_users_globalpermission", "Can add users in global permission"),
            ("delete_users_globalpermission", "Can delete users in global permission"),
        ]
        default_permissions = ('add', 'change', 'delete', 'view', 'list')

    default_permissions = ManyToManyField(
        Permission,
        blank=True,
        help_text="Permissions assigned to all users without exception.",
        limit_choices_to={"content_type__app_label__in": ["service_catalog", "profiles", "resource_tracker_v2", "auth"]}
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(GlobalPermission, self).save(*args, **kwargs)
        self.set_cache()

    def set_cache(self):
        cache.set(self.__class__.__name__, self)

    def get_absolute_url(self):
        return reverse("profiles:globalpermission_rbac")

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        if cache.get(cls.__name__) is None:
            obj, created = GlobalPermission.objects.get_or_create(name="GlobalPermission")
            if not created:
                obj.set_cache()
            return obj
        return cache.get(cls.__name__)

    def get_potential_users(self):
        return User.objects.all()

    def get_scopes(self):
        return AbstractScope.objects.filter(id=self.id)
