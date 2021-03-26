from django.template.defaultfilters import stringfilter
from django.template.defaulttags import register
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django_fsm import can_proceed
from markdown.extensions.toc import TocExtension

from service_catalog.models import Request
from service_catalog.models.instance import InstanceState, Instance
from service_catalog.models.operations import OperationType
from service_catalog.models.request import RequestState

import markdown as md


@register.filter(name='map_instance_state')
def map_instance_state(value):
    map_dict = {
        InstanceState.PENDING: "secondary",
        InstanceState.PROVISIONING: "primary",
        InstanceState.PROVISION_FAILED: "warning",
        InstanceState.AVAILABLE: "success",
        InstanceState.DELETE_FAILED: "warning",
        InstanceState.DELETING: "primary",
        InstanceState.UPDATING: "primary",
        InstanceState.UPDATE_FAILED: "warning",
        InstanceState.DELETED: "danger",
        InstanceState.ARCHIVED: "dark",
    }
    return map_dict[value]


@register.filter(name='map_request_state')
def map_request_state(value):
    map_dict = {
        RequestState.ACCEPTED: "primary",
        RequestState.NEED_INFO: "warning",
        RequestState.SUBMITTED: "info",
        RequestState.REJECTED: "dark",
        RequestState.PROCESSING: "orange",
        RequestState.COMPLETE: "success",
        RequestState.FAILED: "danger",
        RequestState.CANCELED: "light"
    }
    return map_dict[value]


@register.filter(name='map_operation_type')
def map_operation_type(value):
    map_dict = {
        OperationType.CREATE: "success",
        OperationType.UPDATE: "primary",
        OperationType.DELETE: "danger",
    }
    return map_dict[value]


@register.filter(name='is_action_dropdown_disabled')
def is_action_dropdown_disabled(request_id, target_action):
    target_request = Request.objects.get(id=request_id)
    if target_action == "cancel":
        if not can_proceed(target_request.cancel):
            return "disabled"
    if target_action == "need_info":
        if not can_proceed(target_request.need_info):
            return "disabled"
    if target_action == "reject":
        if not can_proceed(target_request.reject):
            return "disabled"
    if target_action == "accept":
        if not can_proceed(target_request.accept):
            return "disabled"
    if target_action == "process":
        if not can_proceed(target_request.process):
            return "disabled"
    if target_action == "re_submit":
        if not can_proceed(target_request.re_submit):
            return "disabled"

    return ""


@register.filter(name='get_action_text_class')
def get_action_text_class(request_id, target_action):
    target_request = Request.objects.get(id=request_id)
    if target_action == "cancel":
        if can_proceed(target_request.cancel):
            return "text-dark"
    if target_action == "need_info":
        if can_proceed(target_request.need_info):
            return "text-warning"
    if target_action == "reject":
        if can_proceed(target_request.reject):
            return "text-danger"
    if target_action == "accept":
        if can_proceed(target_request.accept):
            return "text-primary"
    if target_action == "process":
        if can_proceed(target_request.process):
            return "text-success"
    if target_action == "re_submit":
        if can_proceed(target_request.re_submit):
            return "text-info"
    return ""


@register.filter(name='map_instance_available')
def map_instance_available(instance_id):
    instance = Instance.objects.get(id=instance_id)
    if instance.state == InstanceState.AVAILABLE:
        return ""
    return "disabled"


@register.filter()
@stringfilter
def markdown(content):
    # return md.markdown(value, extensions=['markdown.extensions.extra', 'markdown.extensions.codehilite'])
    md_instance = md.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',  # Indicates code highlighting
        TocExtension(slugify=slugify),
    ])
    md_content = md_instance.convert(content)
    md_content = md_content.replace('<table>', '<table class="table table-bordered">')
    return mark_safe(md_content)
