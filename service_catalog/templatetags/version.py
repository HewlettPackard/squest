from django import template

register = template.Library()


@register.simple_tag
def app_version():
    """
    Return Squest version as listed in `__version__` in `init.py` of settings package
    """
    from Squest.version import __version__
    return __version__
