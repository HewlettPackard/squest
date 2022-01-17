from django import template
from guardian.shortcuts import get_objects_for_user

from service_catalog.models import Request, Support
from service_catalog.models.request import RequestState

register = template.Library()


@register.simple_tag
def submitted_request(user):
    if user.is_staff:
        return Request.objects.filter(state=RequestState.SUBMITTED).count()
    else:
        objects = get_objects_for_user(user, 'service_catalog.view_request')
        return objects.filter(state=RequestState.SUBMITTED).count()


@register.simple_tag
def opened_support(user):
    if user.is_superuser:
        return Support.objects.filter(state='OPENED').count()
    else:
        instances = get_objects_for_user(user, 'service_catalog.request_support_on_instance').distinct()
        return Support.objects.filter(instance__in=instances, state='OPENED').count()
