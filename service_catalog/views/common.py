from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django_fsm import can_proceed
from guardian.shortcuts import get_objects_for_user

from service_catalog.forms import SupportRequestForm
from service_catalog.forms.common_forms import RequestMessageForm, SupportMessageForm
from service_catalog.models import Request, Instance, RequestMessage, Support, SupportMessage
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
        return render(request, 'service_catalog/admin/dashboard.html', context=context)
    else:
        context = {
            "total_request": get_objects_for_user(request.user, 'service_catalog.view_request').filter(state=RequestState.SUBMITTED).count(),
            "total_instance": get_objects_for_user(request.user, 'service_catalog.view_instance').filter(state=InstanceState.AVAILABLE).count(),
        }
        return render(request, 'service_catalog/customer/dashboard.html', context=context)


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
    return render(request, "service_catalog/common/request-comment.html", context)


def instance_new_support(request, instance_id):
    target_instance = get_object_or_404(Instance, id=instance_id)
    parameters = {
        'instance_id': instance_id
    }
    if request.method == 'POST':
        form = SupportRequestForm(request.user, request.POST, **parameters)
        if form.is_valid():
            form.save()
            if request.user.is_superuser:
                return redirect('service_catalog:admin_instance_details', target_instance.id)
            else:
                return redirect('service_catalog:customer_instance_details', target_instance.id)
    else:
        form = SupportRequestForm(request.user, **parameters)

    return render(request, 'service_catalog/common/support-create.html', {'form': form,
                                                          'instance': target_instance})


def instance_support_details(request, instance_id, support_id):
    instance = get_object_or_404(Instance, id=instance_id)
    support = get_object_or_404(Support, id=support_id)
    messages = SupportMessage.objects.filter(support=support)
    if request.method == "POST":
        form = SupportMessageForm(request.POST or None)
        if "btn_close" in request.POST:
            if not can_proceed(support.do_close):
                raise PermissionDenied
            support.do_close()
            support.save()
        if "btn_re_open" in request.POST:
            if not can_proceed(support.do_open):
                raise PermissionDenied
            support.do_open()
            support.save()
        if form.is_valid():
            if form.cleaned_data["content"] is not None and form.cleaned_data["content"] != "":
                new_message = form.save()
                new_message.support = support
                new_message.sender = request.user
                new_message.save()
            if request.user.is_superuser:
                return redirect('service_catalog:admin_instance_support_details', instance.id, support.id)
            else:
                return redirect('service_catalog:customer_instance_support_details', instance.id, support.id)
    else:
        form = SupportMessageForm()

    context = {
        "form": form,
        "instance": instance,
        "messages": messages,
        "support": support
    }
    return render(request, "service_catalog/common/instance-support-details.html", context)
