from django.contrib.contenttypes.models import ContentType
from django.template.defaulttags import register


@register.filter(name='lookup')
def lookup(value, arg):
    return value[arg]


@register.filter
def to_class_name(value):
    return value.__class__.__name__


@register.filter
def to_app_name(value):
    content_type = ContentType.objects.get_for_model(value)
    if content_type.model == "permission":
        return "profiles"
    return content_type.app_label

@register.simple_tag()
def has_perm(user, permission, object):
    return user.has_perm(permission, object)
