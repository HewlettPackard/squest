from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse

from profiles.forms import SupportNotificationFilterForm
from profiles.models import InstanceNotification


@login_required
def support_notification_switch(request):
    request.user.profile.support_notification_enabled = not request.user.profile.support_notification_enabled
    request.user.save()
    return redirect(reverse('profiles:profile') + '#support-notifications')


@user_passes_test(lambda u: u.is_superuser)
def support_notification_create(request):
    if request.method == 'POST':
        form = SupportNotificationFilterForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('profiles:profile') + '#support-notifications')
    else:
        form = SupportNotificationFilterForm(request.user)

    context = {
        'breadcrumbs': [
            {'text': 'Profile', 'url': reverse('profiles:profile') + '#support-notifications'},
            {'text': 'Create a new support notification filter', 'url': ""},
        ],
        'form': form,
        'action': 'create',
        'form_header': 'profiles/forms/form_headers/support_notification_filter_header.html'
    }
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def support_notification_delete(request, support_notification_id):
    support_notification = get_object_or_404(InstanceNotification, id=support_notification_id)
    if support_notification in request.user.profile.instance_notification_filters.all():
        support_notification.delete()
    else:
        raise PermissionDenied
    return redirect(reverse('profiles:profile') + '#support-notifications')


def support_notification_edit(request, support_notification_id):
    support_notification = get_object_or_404(InstanceNotification, id=support_notification_id)
    form = SupportNotificationFilterForm(request.user, request.POST or None, instance=support_notification)
    if form.is_valid():
        form.save()
        return redirect(reverse('profiles:profile') + '#support-notifications')
    context = {
        'form': form,
        'support_notification': support_notification,
        'object_name': "support_notification",
        'breadcrumbs': [
            {'text': 'Profile', 'url': reverse('profiles:profile') + '#support-notifications'},
            {'text': support_notification.name, 'url': ""},
        ],
        'action': "edit"
    }
    return render(request, 'generics/generic_form.html', context)
