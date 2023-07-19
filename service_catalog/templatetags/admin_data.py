from django import template

from service_catalog.models import Request, Support
from service_catalog.models.request import RequestState

register = template.Library()


@register.simple_tag
def submitted_request(user):
    return Request.get_queryset_for_user(user, 'service_catalog.view_request').filter(state=RequestState.SUBMITTED).count()


@register.simple_tag
def opened_support(user):
    return Support.get_queryset_for_user(user, 'service_catalog.view_support').filter(state='OPENED').count()
