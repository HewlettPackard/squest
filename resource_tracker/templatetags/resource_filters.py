from django.template.defaulttags import register

from resource_tracker.models import ResourceAttribute


@register.filter(name='get_attribute_value_from_name')
def get_attribute_value_from_name(resource_id, attribute_name):
    try:
        attribute = ResourceAttribute.objects.get(resource_id=resource_id, name=attribute_name)
        return attribute.value
    except ResourceAttribute.DoesNotExist:
        return ""
