from django.contrib.auth.models import User, Permission
from django.db.models import ManyToManyField
from django.urls import reverse
from profiles.models import AbstractScope
from django.core.cache import cache
default_user_permissions = [
    # Lists
    'service_catalog.list_instance',
    'service_catalog.list_request',
    'service_catalog.list_support',
    'profiles.list_organization',
    'profiles.list_team',
    # Custom link
    'service_catalog.view_customlink',
    # Doc
    'service_catalog.list_doc',
    'service_catalog.view_doc',
    # Portfolio
    'service_catalog.list_portfolio',
    'service_catalog.view_portfolio',
    # Service
    'service_catalog.list_service',
    'service_catalog.view_service',
    # Operation
    'service_catalog.list_operation',
    'service_catalog.view_operation',
    'service_catalog.request_on_service',
    # Request notification
    'profiles.list_requestnotification',
    'profiles.add_requestnotification',
    'profiles.view_requestnotification',
    'profiles.change_requestnotification',
    'profiles.delete_requestnotification',
    # Instance notification
    'profiles.list_instancenotification',
    'profiles.add_instancenotification',
    'profiles.view_instancenotification',
    'profiles.change_instancenotification',
    'profiles.delete_instancenotification',
]



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
            if created:
                codenames = list(map(lambda user_permissions: user_permissions.split('.')[1], default_user_permissions))
                app_labels = list(map(lambda user_permissions: user_permissions.split('.')[0], default_user_permissions))
                obj.user_permissions.add(*Permission.objects.filter(codename__in=codenames, content_type__app_label__in=app_labels))
            else:
                obj.set_cache()
            return obj
        return cache.get(cls.__name__)

    def get_potential_users(self):
        return User.objects.all()

    def get_scopes(self):
        return AbstractScope.objects.filter(id=self.id)
