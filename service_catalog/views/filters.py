from django.template.defaulttags import register
from django_fsm import can_proceed

from service_catalog.models import Request


@register.filter(name='map_instance_state')
def map_instance_state(value):
    map_dict = {
        "PENDING": "secondary",
        "PROVISIONING": "primary",
        "PROVISION_FAILED": "warning",
        "AVAILABLE": "success",
        "DELETE_FAILED": "warning",
        "DELETING": "primary",
        "UPDATING": "primary",
        "UPDATE_FAILED": "warning",
        "DELETED": "danger",
        "ARCHIVED": "dark",
    }
    return map_dict[value]


@register.filter(name='map_request_state')
def map_request_state(value):
    map_dict = {
        "ACCEPTED": "primary",
        "NEED_INFO": "warning",
        "SUBMITTED": "info",
        "REJECTED": "dark",
        "PROCESSING": "orange",
        "COMPLETE": "success",
        "FAILED": "danger",
        "CANCELED": "light"
    }
    return map_dict[value]


@register.filter(name='map_operation_type')
def map_operation_type(value):
    map_dict = {
        "CREATE": "success",
        "UPDATE": "primary",
        "DELETE": "danger",
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
