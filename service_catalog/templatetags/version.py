from django import template

register = template.Library()


@register.simple_tag
def app_version():
    """
    Return Squest version as listed in `__version__` in `init.py` of settings package
    """
    from django.conf import settings
    return settings.SQUEST_VERSION
