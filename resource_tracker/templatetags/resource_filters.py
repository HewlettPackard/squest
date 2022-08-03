from django.template.defaulttags import register

from resource_tracker.models import ResourceAttribute, ResourcePoolAttributeDefinition, \
    ResourceGroupAttributeDefinition, ResourceTextAttribute, ResourceGroupTextAttributeDefinition


@register.filter(name='get_attribute_value_from_name')
def get_attribute_value_from_name(resource, attribute_name):
    try:
        attribute = ResourceAttribute.objects.get(resource=resource,
                                                  attribute_type=ResourceGroupAttributeDefinition.objects.
                                                  get(name=attribute_name,
                                                      resource_group=resource.resource_group))
        return attribute.value
    except ResourceAttribute.DoesNotExist:
        return ""


@register.filter(name='get_text_attribute_value_from_name')
def get_text_attribute_value_from_name(resource, attribute_name):
    try:
        attribute = ResourceTextAttribute.objects.get(resource=resource,
                                                      text_attribute_type=ResourceGroupTextAttributeDefinition.objects.
                                                      get(name=attribute_name,
                                                          resource_group=resource.resource_group))
        return attribute.value
    except ResourceTextAttribute.DoesNotExist:
        return ""


@register.filter(name='get_percent_consumption')
def get_percent_consumption(resource_pool_id, attribute_name):
    try:
        resource_pool_attribute = ResourcePoolAttributeDefinition.objects.get(resource_pool_id=resource_pool_id,
                                                                              name=attribute_name)
        return resource_pool_attribute.percent_consumed
    except ResourcePoolAttributeDefinition.DoesNotExist:
        return 0

@register.filter(name='has_attribute')
def has_attribute(resource_pool_id, attribute_name):
    return ResourcePoolAttributeDefinition.objects.filter(resource_pool_id=resource_pool_id,
                                                          name=attribute_name).exists()


@register.filter(name='subtract')
def subtract(value, arg):
    return value - arg


@register.filter(name='get_total_produced_by')
def get_total_produced_by(resource_poll_attribute, producer):
    return resource_poll_attribute.get_total_produced_by(producer)


@register.filter(name='get_total_consumed_by')
def get_total_consumed_by(resource_poll_attribute, consumer):
    return resource_poll_attribute.get_total_consumed_by(consumer)
