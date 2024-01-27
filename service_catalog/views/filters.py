import json

import markdown as md
from django.conf import settings
from django.contrib.auth.models import User
from django.template.defaultfilters import stringfilter
from django.template.defaulttags import register
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django_fsm import can_proceed
from markdown.extensions.toc import TocExtension

from service_catalog.models import BootstrapType, RequestState, InstanceState
from service_catalog.models import Request
from service_catalog.models.instance import Instance
from service_catalog.models.operations import OperationType
from service_catalog.models.support import SupportState
from .color import map_dict_request_state, map_dict_instance_state, map_dict_step_state


@register.filter(name='map_instance_state')
def map_instance_state(value):
    return map_dict_instance_state[value]


@register.filter(name='map_request_state')
def map_request_state(value):
    return map_dict_request_state[value]


@register.filter(name='map_approvalstep_state')
def map_approvalstep_state(approvalstep):
    return map_dict_step_state[approvalstep.state]


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


@register.filter(name='can_proceed_request_action')
def can_proceed_request_action(args):
    target_action = args.split(',')[0]
    target_request = Request.objects.get(id=args.split(',')[1])
    if target_action == "cancel":
        return can_proceed(target_request.cancel)
    elif target_action == "on_hold":
        return can_proceed(target_request.on_hold)
    elif target_action == "reject":
        return can_proceed(target_request.reject)
    elif target_action == "accept":
        return can_proceed(target_request.accept)
    elif target_action == "process":
        return can_proceed(target_request.process)
    elif target_action == "re_submit":
        return can_proceed(target_request.re_submit)
    elif target_action == "archive":
        return can_proceed(target_request.archive)
    elif target_action == "unarchive":
        return can_proceed(target_request.unarchive)
    return False


@register.simple_tag()
def can_proceed_action(action, instance):
    return can_proceed(instance.__getattribute__(action))


@register.filter(name='can_proceed_instance_action')
def can_proceed_instance_action(args):
    target_action = args.split(',')[0]
    target_instance = Instance.objects.get(id=args.split(',')[1])
    if target_action == 'pending':
        return can_proceed(target_instance.pending)
    elif target_action == 'provision_failed':
        return can_proceed(target_instance.provisioning_has_failed)
    elif target_action == 'provisioning':
        return can_proceed(target_instance.provisioning)
    elif target_action == 'updating':
        return can_proceed(target_instance.updating)
    elif target_action == 'update_failed':
        return can_proceed(target_instance.update_has_failed)
    elif target_action == 'deleting':
        return can_proceed(target_instance.deleting)
    elif target_action == 'deleted':
        return can_proceed(target_instance.deleting)
    elif target_action == 'delete_failed':
        return can_proceed(target_instance.delete_has_failed)
    elif target_action == "archive":
        return can_proceed(target_instance.archive)
    elif target_action == "unarchive":
        return can_proceed(target_instance.unarchive)
    elif target_action == "available":
        return can_proceed(target_instance.available)
    return False


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
    if date_to_format is None:
        return ""
    return date_to_format.astimezone().strftime(settings.DATE_FORMAT)


@register.filter(name="map_color_next_state")
def map_color_next_state(current_state, next_state):
    if current_state == "ON_HOLD":
        return "warning"
    if current_state == next_state:
        return "primary"
    request_state_position = [c[1] for c in RequestState.choices]
    index_of_expected = request_state_position.index(next_state)
    success_list = request_state_position[index_of_expected:]
    if current_state in success_list:
        return "success"
    return "secondary"


@register.filter(name="map_current_state")
def map_current_state(current_state, expected_state):
    request_state_position = [c[1] for c in RequestState.choices]
    index_of_expected = request_state_position.index(expected_state)
    success_list = request_state_position[index_of_expected:]
    if current_state in success_list:
        return "success"
    return "secondary"


@register.filter(name="instance_state_integer_to_string")
def instance_state_integer_to_string(integer_state):
    return InstanceState(integer_state).label


@register.filter(name="display_boolean", is_safe=True)
def display_boolean(boolean_value):
    if boolean_value:
        return mark_safe('<i class="fas fa-circle text-success"></i>')
    else:
        return mark_safe('<i class="fas fa-circle text-secondary"></i>')


@register.simple_tag()
def who_can_approve_on_scope(step, scope):
    return scope.who_has_perm(step.permission.permission_str, exclude_superuser=True)


@register.simple_tag()
def who_can_approve(object):
    return object.who_can_accept(exclude_superuser=True)
