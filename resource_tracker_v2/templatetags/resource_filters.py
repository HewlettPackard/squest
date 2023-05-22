from django.template.defaulttags import register

from resource_tracker_v2.models import ResourceAttribute, AttributeDefinition


@register.filter(name='v2_get_attribute_value_from_name')
def v2_get_attribute_value_from_name(resource, attribute_name):
    try:
        attribute = ResourceAttribute.objects.get(resource=resource,
                                                  attribute_definition=AttributeDefinition.objects.
                                                  get(name=attribute_name))
        return attribute.value
    except ResourceAttribute.DoesNotExist:
        return ""
