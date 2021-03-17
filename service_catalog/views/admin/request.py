from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django_fsm import can_proceed

from service_catalog.forms import NeedInfoForm
from service_catalog.models import Request


@user_passes_test(lambda u: u.is_superuser)
def admin_request_list(request):
    requests = Request.objects.all()
    return render(request, 'admin/request/request-list.html', {'requests': requests})


@user_passes_test(lambda u: u.is_superuser)
def admin_request_cancel(request, request_id):
    target_request = get_object_or_404(Request, id=request_id)
    if request.method == "POST":
        # check that we can delete the request
        if not can_proceed(target_request.cancel):
            raise PermissionDenied
        target_request.cancel()
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
        'request_id': target_request.id
    }
    if request.method == "POST":
        form = NeedInfoForm(request.user, request.POST, **parameters)
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
        form = NeedInfoForm(request.user, **parameters)

    context = {
        "form": form,
        "target_request": target_request
    }
    return render(request, "admin/request/request-need-info.html", context)
