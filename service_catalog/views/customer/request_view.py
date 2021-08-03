from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django_fsm import can_proceed
from guardian.decorators import permission_required_or_403

from service_catalog.mail_utils import send_email_request_canceled
from service_catalog.models import Request
from service_catalog.views import request_comment


@permission_required_or_403('service_catalog.delete_request', (Request, 'id', 'request_id'))
def customer_request_cancel(request, request_id):
    target_request = get_object_or_404(Request, id=request_id)
    if request.method == "POST":
        # check that we can delete the request
        if not can_proceed(target_request.cancel):
            raise PermissionDenied
        target_request.cancel()
        send_email_request_canceled(request_id,
                                    user_applied_state=target_request.user,
                                    request_owner_user=target_request.user)
        # now delete the request
        target_request.delete()
        return redirect('service_catalog:request_list')
    breadcrumbs = [
        {'text': 'Requests', 'url': reverse('service_catalog:request_list')},
        {'text': request_id, 'url': ""},
    ]
    context = {
        'object': target_request,
        'breadcrumbs': breadcrumbs
    }
    return render(request, "service_catalog/customer/request/request-cancel.html", context)


@permission_required_or_403('service_catalog.view_request', (Request, 'id', 'request_id'))
def customer_request_comment(request, request_id):
    breadcrumbs = [
        {'text': 'Requests', 'url': reverse('service_catalog:request_list')},
        {'text': request_id, 'url': ""},
    ]
    return request_comment(request, request_id, 'service_catalog:customer_request_comment', breadcrumbs)
