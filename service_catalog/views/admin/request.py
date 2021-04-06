import logging

import requests
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django_fsm import can_proceed

from service_catalog.filters.request_filter import RequestFilter
from service_catalog.forms import MessageOnRequestForm, AcceptRequestForm
from service_catalog.models import Request
from service_catalog.views import request_comment

logger = logging.getLogger(__name__)


@user_passes_test(lambda u: u.is_superuser)
def admin_request_list(request):
    f = RequestFilter(request.GET, queryset=Request.objects.all())
    return render(request, 'admin/request/request-list.html', {'filter': f})


@user_passes_test(lambda u: u.is_superuser)
def admin_request_cancel(request, request_id):
    target_request = get_object_or_404(Request, id=request_id)
    if request.method == "POST":
        # check that we can delete the request
        if not can_proceed(target_request.cancel):
            raise PermissionDenied
        # now delete the request
        target_request.delete()
        # TODO: notify user
        return redirect(admin_request_list)
    context = {
        "object": target_request
    }
    return render(request, "admin/request/request-cancel.html", context)


@user_passes_test(lambda u: u.is_superuser)
def admin_request_need_info(request, request_id):
    target_request = get_object_or_404(Request, id=request_id)
    parameters = {
        'request_id': target_request.id,
        'message_required': True
    }
    if request.method == "POST":
        form = MessageOnRequestForm(request.user, request.POST, **parameters)
        if form.is_valid():
            # check that we can ask for info the request
            if not can_proceed(target_request.need_info):
                raise PermissionDenied
            form.save()
            target_request.need_info()
            target_request.save()
            # TODO: notify user
            return redirect(admin_request_list)
    else:
        form = MessageOnRequestForm(request.user, **parameters)

    context = {
        "form": form,
        "target_request": target_request
    }
    return render(request, "admin/request/request-need-info.html", context)


@user_passes_test(lambda u: u.is_superuser)
def admin_request_re_submit(request, request_id):
    target_request = get_object_or_404(Request, id=request_id)
    parameters = {
        'request_id': target_request.id,
        'message_required': False
    }
    if request.method == "POST":
        form = MessageOnRequestForm(request.user, request.POST, **parameters)
        if form.is_valid():
            if not can_proceed(target_request.re_submit):
                raise PermissionDenied
            form.save()
            target_request.re_submit()
            target_request.save()
            # TODO: notify user
            return redirect(admin_request_list)
    else:
        form = MessageOnRequestForm(request.user, **parameters)

    context = {
        "form": form,
        "target_request": target_request
    }
    return render(request, "admin/request/request-re-submit.html", context)


@user_passes_test(lambda u: u.is_superuser)
def admin_request_reject(request, request_id):
    target_request = get_object_or_404(Request, id=request_id)
    parameters = {
        'request_id': target_request.id,
        'message_required': True
    }
    if request.method == "POST":
        form = MessageOnRequestForm(request.user, request.POST, **parameters)
        if form.is_valid():
            if not can_proceed(target_request.reject):
                raise PermissionDenied
            form.save()
            target_request.reject()
            target_request.save()
            # TODO: notify user
            return redirect(admin_request_list)
    else:
        form = MessageOnRequestForm(request.user, **parameters)

    context = {
        "form": form,
        "target_request": target_request
    }
    return render(request, "admin/request/request-reject.html", context)


@user_passes_test(lambda u: u.is_superuser)
def admin_request_accept(request, request_id):
    target_request = get_object_or_404(Request, id=request_id)
    parameters = {
        'request_id': request_id
    }
    if request.method == 'POST':
        form = AcceptRequestForm(request.user, request.POST, **parameters)
        if form.is_valid():
            form.save()
            return redirect(admin_request_list)
    else:
        form = AcceptRequestForm(request.user, initial=target_request.fill_in_survey, **parameters)

    context = {
        "form": form,
        "target_request": target_request
    }
    return render(request, 'admin/request/request-accept.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def admin_request_process(request, request_id):
    target_request = get_object_or_404(Request, id=request_id)
    error = False
    error_message = ""
    if request.method == "POST":
        if not can_proceed(target_request.process):
            raise PermissionDenied
        import towerlib
        try:
            # switch the state to processing before trying to execute the process
            target_request.process()
            target_request.save()
            target_request.perform_processing()
            target_request.save()
        except towerlib.towerlibexceptions.AuthFailed:
            error = True
            logger.error("[admin_request_process] Fail to authenticate with provided token when trying "
                         "to process request id '{}'".format(target_request.id))
            error_message = "Fail to authenticate with provided token"
        except requests.exceptions.SSLError:
            error = True
            error_message = "Certificate verify failed"
            logger.error("[admin_request_process] Certificate verify failed when trying "
                         "to process request id '{}'".format(target_request.id))
        except requests.exceptions.ConnectionError:
            error = True
            error_message = "Unable to connect to remote server"
            logger.error("[admin_request_process] Unable to connect to remote server when trying "
                         "to process request id '{}'".format(target_request.id))
        if not error:
            target_request.save()
            # TODO: notify user
            return redirect(admin_request_list)

    context = {
        "target_request": target_request,
        "error_message": error_message
    }
    return render(request, "admin/request/request-process.html", context)


@user_passes_test(lambda u: u.is_superuser)
def admin_request_comment(request, request_id):
    return request_comment(request, request_id, admin_request_comment)

