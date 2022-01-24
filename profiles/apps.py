from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_roles(sender, **kwargs):
    from django.contrib.auth.models import Permission
    from profiles.models import Role
    from django.contrib.contenttypes.models import ContentType
    from profiles.models.rbac import roles_config
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
    # Set the Admin role for each spoc instance
    from service_catalog.models import Instance
    for instance in Instance.objects.all():
        instance.assign_permission_to_spoc()


class ProfilesConfig(AppConfig):
    name = 'profiles'

    def ready(self):
        post_migrate.connect(create_roles, sender=self)
