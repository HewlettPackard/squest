from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse_lazy

from Squest.utils.squest_views import SquestCreateView, SquestUpdateView, SquestDeleteView
from profiles.forms import InstanceNotificationForm
from profiles.models import InstanceNotification


@login_required
def instancenotification_switch(request):
    request.user.profile.instance_notification_enabled = not request.user.profile.instance_notification_enabled
    request.user.save()
    return redirect(reverse_lazy('profiles:profile') + '#instance-notifications')


class InstanceNotificationCreateView(SquestCreateView):
    model = InstanceNotification
    form_class = InstanceNotificationForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_header'] = 'profiles/forms/form_headers/instance_notification_filter_header.html'
        context['breadcrumbs'] = [
            {'text': 'Profile', 'url': reverse_lazy('profiles:profile') + '#instance-notifications'},
            {'text': 'New request notification', 'url': ""},
        ]
        return context


class InstanceNotificationDeleteView(SquestDeleteView):
    model = InstanceNotification

    def get_success_url(self):
        return f"{reverse_lazy('profiles:profile')}#instance-notifications"

    def get_queryset(self):
        return InstanceNotification.objects.filter(profile=self.request.user.profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Profile', 'url': reverse_lazy('profiles:profile') + '#instance-notifications'},
            {'text': self.get_object(), 'url': ""},
            {'text': "Delete", 'url': ""},
        ]
        return context


class InstanceNotificationEditView(SquestUpdateView):
    model = InstanceNotification
    form_class = InstanceNotificationForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        return InstanceNotification.objects.filter(profile=self.request.user.profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_header'] = 'profiles/forms/form_headers/request_notification_filter_header.html'
        context['breadcrumbs'] = [
            {'text': 'Profile', 'url': reverse_lazy('profiles:profile') + '#instance-notifications'},
            {'text': self.get_object(), 'url': ""},
            {'text': "Edit", 'url': ""},
        ]
        return context
