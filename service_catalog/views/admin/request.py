from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django_fsm import can_proceed

from service_catalog.models import Request, Instance


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
        # delete the related instance (we should have only one)
        instance = Instance.objects.get(request=target_request)
        instance.delete()
        # now delete the request
        target_request.delete()
        # TODO: notify user
        return redirect(admin_request_list)
    context = {
        "object": target_request
    }
    return render(request, "admin/request/request-cancel.html", context)
