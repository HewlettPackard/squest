from django import template

from service_catalog.models import Request, Support
from service_catalog.models.request import RequestState

register = template.Library()


@register.simple_tag
def submitted_request():
    return Request.objects.filter(state=RequestState.SUBMITTED).count()


@register.simple_tag
def opened_support():
    return Support.objects.filter(state='OPENED').count()
