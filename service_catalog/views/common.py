from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from guardian.shortcuts import get_objects_for_user

from service_catalog.forms.common_forms import RequestMessageForm
from service_catalog.models import Request, Instance, Message, RequestMessage
from service_catalog.models.instance import InstanceState
from service_catalog.models.request import RequestState


@login_required
def home(request):
    if request.user.is_superuser:
        context = {
            "total_request": Request.objects.filter(state=RequestState.SUBMITTED).count(),
            "total_instance": Instance.objects.filter(state="AVAILABLE").count(),
            "total_user": User.objects.all().count()
        }
        return render(request, 'admin/dashboard.html', context=context)
    else:
        context = {
            "total_request": get_objects_for_user(request.user, 'service_catalog.view_request').filter(state=RequestState.SUBMITTED).count(),
            "total_instance": get_objects_for_user(request.user, 'service_catalog.view_instance').filter(state=InstanceState.AVAILABLE).count(),
        }
        return render(request, 'customer/dashboard.html', context=context)


def request_comment(request, request_id, redirect_to_view):
    target_request = get_object_or_404(Request, id=request_id)
    messages = RequestMessage.objects.filter(request=target_request)
    if request.method == "POST":
        form = RequestMessageForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            new_message = form.save()
            new_message.request = target_request
            new_message.sender = request.user
            new_message.save()
            return redirect(redirect_to_view, target_request.id)
    else:
        form = RequestMessageForm()

    context = {
        "form": form,
        "target_request": target_request,
        "messages": messages
    }
    return render(request, "common/request-comment.html", context)
