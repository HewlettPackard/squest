import json

from django.conf import settings
from django.contrib.auth.models import User
from django.template.defaultfilters import stringfilter
from django.template.defaulttags import register
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django_fsm import can_proceed
from markdown.extensions.toc import TocExtension

from service_catalog.models import Request
from service_catalog.models.instance import InstanceState, Instance
from service_catalog.models.operations import OperationType
import markdown as md

from service_catalog.models.support import SupportState

from .color import map_dict_request_state, map_dict_instance_state
from service_catalog.models import BootstrapType


@register.filter(name='map_instance_state')
def map_instance_state(value):
    return map_dict_instance_state[value]


@register.filter(name='map_request_state')
def map_request_state(value):
    return map_dict_request_state[value]


@register.filter(name='map_operation_type')
def map_operation_type(value):
    map_dict = {
        OperationType.CREATE: "success",
        OperationType.UPDATE: "primary",
        OperationType.DELETE: "danger",
    }
    return map_dict[value]


@register.filter(name='map_color_to_icon')
def map_color_to_icon(value):
    map_dict = {
        BootstrapType.DANGER: "fas fa-ban",
        BootstrapType.INFO: "fas fa-info",
        BootstrapType.WARNING: "fas fa-exclamation-triangle",
        BootstrapType.SUCCESS: "fas fa-check",
    }
    return map_dict[value]


@register.filter(name='is_action_dropdown_disabled')
def is_action_dropdown_disabled(args):
    target_action = args.split(',')[0]
    user = User.objects.get(id=int(args.split(',')[1]))
    target_request = Request.objects.get(id=args.split(',')[2])
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
    if target_action == "archive":
        if not can_proceed(target_request.archive):
            return "disabled"
    if target_action == "unarchive":
        if not can_proceed(target_request.unarchive):
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
    if target_action == "archive":
        if can_proceed(target_request.archive):
            return "text-black"
    if target_action == "unarchive":
        if can_proceed(target_request.unarchive):
            return "text-success"
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


@register.filter(name='map_support_state')
def map_support_state(value):
    map_dict = {
        SupportState.OPENED: "success",
        SupportState.CLOSED: "danger"
    }
    return map_dict[value]


@register.filter(name="pretty_json")
def pretty_json(value):
    return json.dumps(value, indent=4)


@register.filter
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)


@register.filter(name="squest_date_format")
def squest_date_format(date_to_format):
    return date_to_format.strftime(settings.DATE_FORMAT)


@register.filter(name="get_field_type")
def get_field_type(instance):
    for survey in instance.operation.job_template.survey["spec"]:
        if survey["question_name"] == instance.name:
            return survey["type"]
    return ""
