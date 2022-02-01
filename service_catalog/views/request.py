from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_fsm import can_proceed

from guardian.decorators import permission_required_or_403
from guardian.shortcuts import get_objects_for_user

from service_catalog.forms import RequestMessageForm
from service_catalog.models import Request, RequestMessage
from service_catalog.models.instance import InstanceState
from service_catalog.mail_utils import send_email_request_canceled


@login_required
@permission_required_or_403('service_catalog.cancel_request', (Request, 'id', 'request_id'))
def request_cancel(request, request_id):
    target_request = get_object_or_404(Request, id=request_id)
    if request.method == "POST":
        # check that we can cancel the request
        if not can_proceed(target_request.cancel):
            raise PermissionDenied
        send_email_request_canceled(target_request,
                                    user_applied_state=request.user,
                                    request_owner_user=target_request.user)

        if target_request.cancel():
            target_request.save()
        return redirect('service_catalog:request_list')
    breadcrumbs = [
        {'text': 'Requests', 'url': reverse('service_catalog:request_list')},
        {'text': request_id, 'url': ""},
    ]
    context = {
        'breadcrumbs': breadcrumbs,
        'confirm_text': mark_safe(f"Do you want to cancel the request <strong>{target_request.id}</strong>?"),
        'action_url': reverse('service_catalog:request_cancel', kwargs={'request_id': request_id}),
        'button_text': 'Confirm cancel request',
        'details': {
            'warning_sentence': f"Canceling this request will delete the instance {target_request.instance.name}."
        } if target_request.instance.state == InstanceState.PENDING else None
    }
    return render(request, "generics/confirm-delete-template.html", context)


@login_required
@permission_required_or_403('service_catalog.comment_request', (Request, 'id', 'request_id'))
def request_comment(request, request_id):
    breadcrumbs = [
        {'text': 'Requests', 'url': reverse('service_catalog:request_list')},
        {'text': request_id, 'url': ""},
    ]
    target_request = get_object_or_404(Request, id=request_id)
    messages = RequestMessage.objects.filter(request=target_request)
    if request.method == "POST":
        form = RequestMessageForm(request.POST or None, request.FILES or None, sender=request.user,
                                  target_request=target_request)
        if form.is_valid():
            form.save()
            return redirect('service_catalog:request_comment', target_request.id)
    else:
        form = RequestMessageForm(sender=request.user, target_request=target_request)
    context = {
        'form': form,
        'target_request': target_request,
        'messages': messages,
        'breadcrumbs': breadcrumbs
    }
    return render(request, "service_catalog/common/request-comment.html", context)


@login_required
def request_details(request, request_id):
    request_list = get_objects_for_user(request.user, 'service_catalog.view_request')
    target_request = get_object_or_404(request_list, id=request_id)
    context = {'target_request': target_request,
               'breadcrumbs': [
                   {'text': 'Requests', 'url': reverse('service_catalog:request_list')},
                   {'text': request_id, 'url': ""},
               ],
               }
    return render(request, 'service_catalog/common/request-details.html', context=context)
