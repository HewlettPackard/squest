from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django_fsm import can_proceed
from django.template.defaulttags import register
from guardian.decorators import permission_required_or_403
from guardian.shortcuts import get_objects_for_user

from service_catalog.models import Request, Instance


@register.filter(name='map_badge_request_state')
def map_badge_request_state(value):
    map_dict = {
        "ACCEPTED": "bg-primary",
        "NEED_INFO": "bg-warning",
        "SUBMITTED": "bg-secondary",
        "REJECTED": "bg-dark",
        "PROCESSING": "bg-primary",
        "COMPLETE": "bg-success",
        "FAILED": "bg-danger",
        "CANCELED": "bg-light"
    }
    return map_dict[value]


@register.filter(name='map_badge_operation_type')
def map_badge_operation_type(value):
    map_dict = {
        "CREATE": "bg-success",
        "UPDATE": "bg-primary",
        "DELETE": "bg-danger",
    }
    return map_dict[value]


@login_required
def customer_request_list(request):
    requests = get_objects_for_user(request.user, 'service_catalog.view_request')
    return render(request, 'customer/request/request-list.html', {'requests': requests})


@permission_required_or_403('service_catalog.delete_request', (Request, 'id', 'request_id'))
def customer_request_cancel(request, request_id):
    target_request = get_object_or_404(Request, id=request_id)
    if request.method == "POST":
        # check that we can delete the request
        if not can_proceed(target_request.cancel):
            raise PermissionDenied
        target_request.cancel()
        # delete the related instance (we should have only one)
        instance = Instance.objects.get(request=target_request)
        instance.delete()
        # now delete the request
        target_request.delete()
        return redirect(customer_request_list)
    context = {
        "object": target_request
    }
    return render(request, "customer/request/request-cancel.html", context)
