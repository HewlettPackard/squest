import logging

from django.apps import AppConfig
from django.db.models.signals import post_migrate

logger = logging.getLogger(__name__)

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


def create_roles(sender, **kwargs):
    logger.info("create_roles method called")
    from django.contrib.auth.models import Permission
    from profiles.models import Role
    from profiles.models.default_rbac import roles_list
    from django.contrib.contenttypes.models import ContentType
    for role_name, role_params in roles_list.items():
        role, created = Role.objects.get_or_create(
            name=role_name,
            description=role_params['description'],
        )
        for model_name, model_params in role_params['model_names'].items():
            content_type = ContentType.objects.get(app_label=model_name.split('.')[0], model=model_name.split('.')[1])
            for codename in model_params['permissions']:
                permission, created = Permission.objects.get_or_create(codename=codename, content_type=content_type)
                role.permissions.add(permission)


def insert_default_user_permissions(sender, **kwargs):
    from profiles.models import GlobalPermission
    from django.contrib.auth.models import Permission
    global_permission, created = GlobalPermission.objects.get_or_create(name="GlobalPermission")
    if created:
        codenames = list(
            map(lambda user_permissions: user_permissions.split('.')[1], default_user_permissions))
        app_labels = list(
            map(lambda user_permissions: user_permissions.split('.')[0], default_user_permissions))
        global_permission.user_permissions.add(
            *Permission.objects.filter(
                codename__in=codenames,
                content_type__app_label__in=app_labels
            )
        )


class ProfilesConfig(AppConfig):
    name = 'profiles'

    def ready(self):
        post_migrate.connect(create_roles, sender=self)
        post_migrate.connect(insert_default_user_permissions, sender=self)
