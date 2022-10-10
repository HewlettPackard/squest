from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse

from profiles.forms.request_notification_filter_forms import RequestNotificationFilterForm
from profiles.models import RequestNotification


@login_required
def request_notification_switch(request):
    request.user.profile.request_notification_enabled = not request.user.profile.request_notification_enabled
    request.user.save()
    return redirect(reverse('profiles:profile') + '#request-notifications')


@user_passes_test(lambda u: u.is_superuser)
def request_notification_create(request):
    if request.method == 'POST':
        form = RequestNotificationFilterForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('profiles:profile') + '#request-notifications')
    else:
        form = RequestNotificationFilterForm(request.user)

    context = {
        'breadcrumbs': [
            {'text': 'Profile', 'url': reverse('profiles:profile') + '#request-notifications'},
            {'text': 'Create a new request notification filter', 'url': ""},
        ],
        'form': form,
        'action': 'create',
        'form_header': 'profiles/forms/form_headers/request_notification_filter_header.html'
    }
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def request_notification_delete(request, request_notification_id):
    request_notification = get_object_or_404(RequestNotification, id=request_notification_id)
    if request_notification in request.user.profile.request_notification_filters.all():
        request_notification.delete()
    else:
        raise PermissionDenied
    return redirect(reverse('profiles:profile') + '#request-notifications')


def request_notification_edit(request, request_notification_id):
    request_notification = get_object_or_404(RequestNotification, id=request_notification_id)
    form = RequestNotificationFilterForm(request.user, request.POST or None, instance=request_notification)
    if form.is_valid():
        form.save()
        return redirect(reverse('profiles:profile') + '#request-notifications')
    context = {
        'form': form,
        'request_notification': request_notification,
        'object_name': "request_notification",
        'breadcrumbs': [
            {'text': 'Profile', 'url': reverse('profiles:profile') + '#request-notifications'},
            {'text': request_notification.name, 'url': ""},
        ],
        'action': "edit"
    }
    return render(request, 'generics/generic_form.html', context)
