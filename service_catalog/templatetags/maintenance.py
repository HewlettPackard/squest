from django import template
from django.conf import settings

from service_catalog.models import SquestSettings

register = template.Library()


@register.simple_tag()
def is_maintenance_mode_enabled():
    return SquestSettings.load().maintenance_mode_enabled


@register.simple_tag()
def is_dev_server():
    return settings.IS_DEV_SERVER
