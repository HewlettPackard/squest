from django import template

from service_catalog.models import SquestSettings

register = template.Library()


@register.simple_tag()
def is_maintenance_mode_enabled():
    return SquestSettings.load().maintenance_mode_enabled
