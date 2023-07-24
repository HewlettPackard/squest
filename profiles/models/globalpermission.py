from django.contrib.auth.models import User, Permission
from django.core.cache import cache
from django.db.models import ManyToManyField
from django.urls import reverse

from profiles.models import AbstractScope


class GlobalPermission(AbstractScope):
    class Meta:
        permissions = [
            ("view_users_team", "Can view users in team"),
            ("add_users_team", "Can add users in team"),
            ("delete_users_team", "Can delete users in team"),
        ]
        default_permissions = ('add', 'change', 'delete', 'view', 'list')

    user_permissions = ManyToManyField(
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
        return reverse("profiles:globalpermission_details")

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
