import logging

import requests
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_fsm import can_proceed
from guardian.shortcuts import get_objects_for_user

from service_catalog.forms import RequestMessageForm, AcceptRequestForm
from service_catalog.mail_utils import send_mail_request_update
from service_catalog.models import Request

logger = logging.getLogger(__name__)


@user_passes_test(lambda u: u.is_superuser)
def admin_request_need_info(request, request_id):
    target_request = get_object_or_404(Request, id=request_id)
    if not can_proceed(target_request.need_info):
        raise PermissionDenied
    if request.method == "POST":
        form = RequestMessageForm(request.POST or None, request.FILES or None, sender=request.user,
                                  target_request=target_request)
        if form.is_valid():
            message = form.save(send_notification=False)
            target_request.need_info()
            target_request.save()
            send_mail_request_update(target_request, user_applied_state=request.user, message=message)
            return redirect('service_catalog:request_list')
    else:
        form = RequestMessageForm(sender=request.user, target_request=target_request)
    breadcrumbs = [
        {'text': 'Requests', 'url': reverse('service_catalog:request_list')},
        {'text': request_id, 'url': ""},
    ]
    context = {
        'form': form,
        'target_request': target_request,
        'breadcrumbs': breadcrumbs
    }
    return render(request, "service_catalog/admin/request/request-need-info.html", context)


@user_passes_test(lambda u: u.is_superuser)
def admin_request_re_submit(request, request_id):
    target_request = get_object_or_404(Request, id=request_id)
    if not can_proceed(target_request.re_submit):
        raise PermissionDenied
    if request.method == "POST":
        form = RequestMessageForm(request.POST or None, request.FILES or None, sender=request.user,
                                  target_request=target_request)
        if form.is_valid():
            message = form.save(send_notification=False)
            target_request.re_submit()
            target_request.save()
            send_mail_request_update(target_request, user_applied_state=request.user, message=message)
            return redirect('service_catalog:request_list')
    else:
        form = RequestMessageForm(sender=request.user, target_request=target_request)
    breadcrumbs = [
        {'text': 'Requests', 'url': reverse('service_catalog:request_list')},
        {'text': request_id, 'url': ""},
    ]
    context = {
        'form': form,
        'target_request': target_request,
        'breadcrumbs': breadcrumbs
    }
    return render(request, "service_catalog/admin/request/request-re-submit.html", context)


@user_passes_test(lambda u: u.is_superuser)
def admin_request_reject(request, request_id):
    target_request = get_object_or_404(Request, id=request_id)
    if not can_proceed(target_request.reject):
        raise PermissionDenied
    if request.method == "POST":
        form = RequestMessageForm(request.POST or None, request.FILES or None, sender=request.user,
                                  target_request=target_request)
        if form.is_valid():
            message = form.save(send_notification=False)
            target_request.reject()
            target_request.save()
            send_mail_request_update(target_request, user_applied_state=request.user, message=message)
            return redirect('service_catalog:request_list')
    else:
        form = RequestMessageForm(sender=request.user, target_request=target_request)
    breadcrumbs = [
        {'text': 'Requests', 'url': reverse('service_catalog:request_list')},
        {'text': request_id, 'url': ""},
    ]
    context = {
        'form': form,
        'target_request': target_request,
        'breadcrumbs': breadcrumbs
    }
    return render(request, "service_catalog/admin/request/request-reject.html", context)


@user_passes_test(lambda u: u.is_superuser)
def admin_request_accept(request, request_id):
    target_request = get_object_or_404(Request, id=request_id)
    if not can_proceed(target_request.accept):
        raise PermissionDenied
    parameters = {
        'request': target_request
    }
    if request.method == 'POST':
        form = AcceptRequestForm(request.user, request.POST, **parameters)
        if form.is_valid():
            form.save()
            target_request.refresh_from_db()
            send_mail_request_update(target_request, user_applied_state=request.user)
            return redirect('service_catalog:request_list')
    else:
        form = AcceptRequestForm(request.user, initial=target_request.fill_in_survey, **parameters)
    breadcrumbs = [
        {'text': 'Requests', 'url': reverse('service_catalog:request_list')},
        {'text': request_id, 'url': ""},
    ]
    context = {
        'form': form,
        'target_request': target_request,
        'breadcrumbs': breadcrumbs
    }
    return render(request, 'service_catalog/admin/request/request-accept.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def admin_request_process(request, request_id):
    target_request = get_object_or_404(Request, id=request_id)
    if not can_proceed(target_request.process):
        raise PermissionDenied
    error_message = ""
    if request.method == "POST":
        error_message = process_request(request.user, target_request)
        if not error_message:
            return redirect('service_catalog:request_list')
    breadcrumbs = [
        {'text': 'Requests', 'url': reverse('service_catalog:request_list')},
        {'text': request_id, 'url': ""},
    ]
    context = {
        'target_request': target_request,
        'error_message': error_message,
        'breadcrumbs': breadcrumbs
    }
    return render(request, "service_catalog/admin/request/request-process.html", context)


@login_required
def request_details(request, request_id):
    request_list = get_objects_for_user(request.user, 'service_catalog.view_request')
    target_request = get_object_or_404(request_list, id=request_id)
    breadcrumbs = [
        {'text': 'Requests', 'url': reverse('service_catalog:request_list')},
        {'text': request_id, 'url': ""},
    ]
    context = {'target_request': target_request,
               'breadcrumbs': breadcrumbs,
               }
    return render(request, 'service_catalog/common/request-details.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def admin_request_archive(request, request_id):
    target_request = get_object_or_404(Request, id=request_id)
    if not can_proceed(target_request.archive):
        raise PermissionDenied
    target_request.archive()
    target_request.save()
    return redirect('service_catalog:request_list')


@user_passes_test(lambda u: u.is_superuser)
def admin_request_unarchive(request, request_id):
    target_request = get_object_or_404(Request, id=request_id)
    if not can_proceed(target_request.unarchive):
        raise PermissionDenied
    target_request.unarchive()
    target_request.save()
    return redirect('service_catalog:request_list')


@user_passes_test(lambda u: u.is_superuser)
def request_delete(request, request_id):
    target_request = get_object_or_404(Request, id=request_id)
    parameters = {
        'request_id': request_id
    }
    if request.method == 'POST':
        target_request.delete()
        return redirect("service_catalog:request_list")
    breadcrumbs = [
        {'text': 'Requests', 'url': reverse('service_catalog:request_list')},
        {'text': request_id, 'url': ""},
        {'text': "Delete", 'url': ""},
    ]
    context = {
        'breadcrumbs': breadcrumbs,
        'confirm_text': mark_safe(f"Confirm deletion of request <strong>{target_request.id}</strong>?"),
        'action_url': reverse('service_catalog:request_delete', kwargs=parameters),
        'button_text': 'Delete'
    }
    return render(request, 'generics/confirm-delete-template.html', context=context)


def process_request(user, target_request):
    from towerlib.towerlibexceptions import AuthFailed
    try:
        # switch the state to processing before trying to execute the process
        target_request.process()
        target_request.save()
        target_request.perform_processing()
        target_request.save()
    except AuthFailed:
        logger.error(
            f"[admin_request_process] Fail to authenticate with provided token when trying to process request "
            f"id '{target_request.id}'")
        return "Fail to authenticate with provided token"
    except requests.exceptions.SSLError:
        logger.error(
            f"[admin_request_process] Certificate verify failed when trying to process request "
            f"id '{target_request.id}'")
        return "Certificate verify failed"
    except requests.exceptions.ConnectionError:
        logger.error(
            f"[admin_request_process] Unable to connect to remote server when trying to process request "
            f"id '{target_request.id}'")
        return "Unable to connect to remote server"
    target_request.save()
    send_mail_request_update(target_request, user_applied_state=user)
    return ""
