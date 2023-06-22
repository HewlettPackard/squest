import logging

from django.apps import AppConfig
from django.db.models.signals import post_migrate

logger = logging.getLogger(__name__)

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
            print(model_name)
            content_type = ContentType.objects.get(app_label=model_name.split('.')[0], model=model_name.split('.')[1])
            for codename in model_params['permissions']:
                permission, created = Permission.objects.get_or_create(codename=codename, content_type=content_type)
                role.permissions.add(permission)




class ProfilesConfig(AppConfig):
    name = 'profiles'

    def ready(self):
        post_migrate.connect(create_roles, sender=self)
