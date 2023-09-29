import logging

from django.apps import AppConfig
from django.db.models.signals import post_migrate

logger = logging.getLogger(__name__)


def create_roles(sender, **kwargs):
    logger.info("create_roles method called")
    from profiles.models import Role
    from profiles.default_rbac.default_roles import default_roles
    from profiles.models.squest_permission import Permission

    role_migration_filter = Role.objects.filter(name="Squest user migration/0014_auto_20230622_1722")
    if role_migration_filter.exists():
        role_migration = role_migration_filter.first()
        role_migration.name = "Squest user"
        role_migration.save()
        codenames = list(
            map(lambda x: x.split('.')[1],
                default_roles[role_migration.name]['permissions']))
        app_labels = list(
            map(lambda x: x.split('.')[0],
                default_roles[role_migration.name]['permissions']))
        role_migration.permissions.add(
            *Permission.objects.filter(
                codename__in=codenames,
                content_type__app_label__in=app_labels
            )
        )

    for role_name, role_params in default_roles.items():
        role, created = Role.objects.get_or_create(
            name=role_name,
            description=role_params['description'],
        )
        if created:
            codenames = list(
                map(lambda x: x.split('.')[1], role_params['permissions'])
            )
            app_labels = list(
                map(lambda x: x.split('.')[0], role_params['permissions'])
            )
            role.permissions.add(
                *Permission.objects.filter(
                    codename__in=codenames,
                    content_type__app_label__in=app_labels
                )
            )


class ProfilesConfig(AppConfig):
    name = 'profiles'

    def ready(self):
        post_migrate.connect(create_roles, sender=self)
