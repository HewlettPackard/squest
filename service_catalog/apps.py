import logging
import sys

from django.apps import AppConfig
from django.db.models.signals import post_migrate

logger = logging.getLogger(__name__)


def create_default_token(sender=None, **kwargs):
    logger.info("create_default_token method called")
    from django.conf import settings
    from django.contrib.auth.models import User
    from profiles.models import Token
    if settings.DEFAULT_ADMIN_TOKEN is not None:
        try:
            admin_user = User.objects.get(username="admin")
            if not Token.objects.filter(key=settings.DEFAULT_ADMIN_TOKEN).exists():
                Token.objects.create(key=settings.DEFAULT_ADMIN_TOKEN,
                                     user=admin_user,
                                     description="DEFAULT_ADMIN_TOKEN")
                logger.info("Default admin token inserted")
        except User.DoesNotExist:
            pass

def create_default_password(sender=None, **kwargs):
    logger.info("create_default_password method called")
    from django.conf import settings
    from django.contrib.auth.models import User
    if settings.DEFAULT_ADMIN_PASSWORD is not None:
        try:
            admin_user = User.objects.get(username="admin")
            admin_user.set_password(settings.DEFAULT_ADMIN_PASSWORD)
            admin_user.save()
        except User.DoesNotExist:
            pass


class ServiceCatalogConfig(AppConfig):
    name = 'service_catalog'

    def ready(self):
        post_migrate.connect(create_default_token, sender=self)
        post_migrate.connect(create_default_password, sender=self)

