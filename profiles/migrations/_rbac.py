from django.apps.registry import apps as global_apps
from django.contrib.auth.models import Permission

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.management import create_contenttypes
from django.contrib.auth.management import create_permissions

from profiles.models import Role
from profiles.models.rbac import roles_config


def create_roles(apps, schema_editor):
    """
    This method create all default role which are group of permissions defined in models/rbac.py
    """
    for app_config in global_apps.get_app_configs():
        create_contenttypes(app_config, verbosity=0)
        app_config.models_module = True
        create_permissions(app_config, verbosity=0)
        app_config.models_module = None
    for model_name, roles in roles_config.items():
        content_type = ContentType.objects.get(app_label=model_name.split('.')[0], model=model_name.split('.')[1])
        for role_name, role_params in roles.items():
            role, created = Role.objects.get_or_create(
                name=role_name,
                description=role_params['description'],
                content_type=content_type
            )
            for codename in role_params['permissions']:
                permission, created = Permission.objects.get_or_create(codename=codename, content_type=content_type)
                role.permissions.add(permission)
