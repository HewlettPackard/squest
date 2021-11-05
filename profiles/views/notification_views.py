from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse

from profiles.forms.notification_forms import NotificationServiceForm
from service_catalog.models import Service


@login_required
def notification_switch(request):
    request.user.profile.notification_enabled = not request.user.profile.notification_enabled
    request.user.save()
    return redirect(reverse('profiles:profile') + '#notifications')


@user_passes_test(lambda u: u.is_superuser)
def notification_add_service(request):
    if request.method == 'POST':
        form = NotificationServiceForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('profiles:profile') + '#notifications')
    else:
        form = NotificationServiceForm(request.user)

    context = {'form': form, 'action': 'create'}
    return render(request, 'profiles/notification-service-add.html', context)


@user_passes_test(lambda u: u.is_superuser)
def notification_remove_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    request.user.profile.subscribed_services_notification.remove(service)
    request.user.save()
    return redirect(reverse('profiles:profile') + '#notifications')
