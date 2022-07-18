from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse

from profiles.forms.notification_filter_forms import NotificationFilterForm
from profiles.models import NotificationFilter


@login_required
def notification_switch(request):
    request.user.profile.notification_enabled = not request.user.profile.notification_enabled
    request.user.save()
    return redirect(reverse('profiles:profile') + '#notifications')


@user_passes_test(lambda u: u.is_superuser)
def notification_filter_create(request):
    if request.method == 'POST':
        form = NotificationFilterForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('profiles:profile') + '#notifications')
    else:
        form = NotificationFilterForm(request.user)

    context = {
        'breadcrumbs': [
            {'text': 'Profile', 'url': reverse('profiles:profile') + '#notifications'},
            {'text': 'Create a new notification filter', 'url': ""},
        ],
        'form': form,
        'action': 'create',
        'form_header': 'profiles/forms/form_headers/notification_filter_header.html'
    }
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def notification_filter_delete(request, notification_filter_id):
    notification_filter = get_object_or_404(NotificationFilter, id=notification_filter_id)
    if notification_filter in request.user.profile.notification_filters.all():
        notification_filter.delete()
    else:
        raise PermissionDenied
    return redirect(reverse('profiles:profile') + '#notifications')


def notification_filter_edit(request, notification_filter_id):
    notification_filter = get_object_or_404(NotificationFilter, id=notification_filter_id)
    form = NotificationFilterForm(request.user, request.POST or None, instance=notification_filter)
    if form.is_valid():
        form.save()
        return redirect(reverse('profiles:profile') + '#notifications')
    context = {
        'form': form,
        'notification_filter': notification_filter,
        'object_name': "notification_filter",
        'breadcrumbs': [
            {'text': 'Profile', 'url': reverse('profiles:profile') + '#notifications'},
            {'text': notification_filter.name, 'url': ""},
        ],
        'action': "edit"
    }
    return render(request, 'generics/generic_form.html', context)
