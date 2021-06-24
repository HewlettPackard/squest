from django.template.defaulttags import register

from resource_tracker.models import ResourceAttribute, ResourcePoolAttributeDefinition


@register.filter(name='get_attribute_value_from_name')
def get_attribute_value_from_name(resource_id, attribute_name):
    try:
        attribute = ResourceAttribute.objects.get(resource_id=resource_id, name=attribute_name)
        return attribute.value
    except ResourceAttribute.DoesNotExist:
        return ""


@register.filter(name='get_percent_consumption')
def get_percent_consumption(resource_pool_id, attribute_name):
    try:
        resource_pool_attribute = ResourcePoolAttributeDefinition.objects.get(resource_pool_id=resource_pool_id,
                                                                              name=attribute_name)
        return resource_pool_attribute.get_percent_consumed()
    except ResourcePoolAttributeDefinition.DoesNotExist:
        return 0


@register.filter(name='get_total_produced')
def get_total_produced(resource_pool_id, attribute_name):
    try:
        resource_pool_attribute = ResourcePoolAttributeDefinition.objects.get(resource_pool_id=resource_pool_id,
                                                                              name=attribute_name)
        return resource_pool_attribute.get_total_produced()
    except ResourcePoolAttributeDefinition.DoesNotExist:
        return 0


@register.filter(name='get_total_consumed')
def get_total_consumed(resource_pool_id, attribute_name):
    try:
        resource_pool_attribute = ResourcePoolAttributeDefinition.objects.get(resource_pool_id=resource_pool_id,
                                                                              name=attribute_name)
        return resource_pool_attribute.get_total_consumed()
    except ResourcePoolAttributeDefinition.DoesNotExist:
        return 0


@register.filter(name='get_progress_bar_color')
def get_progress_bar_color(resource_pool_id, attribute_name):
    total_consumed = get_percent_consumption(resource_pool_id, attribute_name)
    if total_consumed < 80:
        return "bg-green"
    if 80 < total_consumed < 90:
        return "bg-yellow"
    return "bg-red"


@register.filter(name='has_attribute')
def has_attribute(resource_pool_id, attribute_name):
    return ResourcePoolAttributeDefinition.objects.filter(resource_pool_id=resource_pool_id,
                                                          name=attribute_name).exists()
