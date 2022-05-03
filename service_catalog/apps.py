import logging

from django.apps import AppConfig


logger = logging.getLogger(__name__)


def create_default_token():
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


class ServiceCatalogConfig(AppConfig):
    name = 'service_catalog'

    def ready(self):
        create_default_token()
