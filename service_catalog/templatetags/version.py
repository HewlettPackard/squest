from django import template

register = template.Library()


@register.simple_tag
def commit_sha():
    """
    Return Squest 6 first characters of commit SHA.
    """
    from django.conf import settings
    return settings.SQUEST_COMMIT_SHA6


@register.simple_tag
def squest_version():
    """
    Return Squest version as listed in `__version__` in `init.py` of settings package
    """
    from Squest.version import __version__
    return __version__
