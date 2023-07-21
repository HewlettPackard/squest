from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from Squest.utils.squest_views import *
from profiles.forms.request_notification_form import RequestNotificationForm
from profiles.models import RequestNotification


@login_required
def requestnotification_switch(request):
    request.user.profile.request_notification_enabled = not request.user.profile.request_notification_enabled
    request.user.save()
    return redirect(reverse_lazy('profiles:profile') + '#request-notifications')


class RequestNotificationCreateView(SquestCreateView):
    model = RequestNotification
    form_class = RequestNotificationForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_header'] = 'profiles/forms/form_headers/request_notification_filter_header.html'
        context['breadcrumbs'] = [
            {'text': 'Profile', 'url': reverse_lazy('profiles:profile') + '#request-notifications'},
            {'text': 'New request notification', 'url': ""},
        ]
        return context


class RequestNotificationDeleteView(SquestDeleteView):
    model = RequestNotification

    def get_success_url(self):
        return f"{reverse_lazy('profiles:profile')}#request-notifications"

    def get_queryset(self):
        return RequestNotification.objects.filter(profile=self.request.user.profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Profile', 'url': reverse_lazy('profiles:profile') + '#request-notifications'},
            {'text': self.get_object(), 'url': self.get_object().get_absolute_url()},
            {'text': 'Delete', 'url': ""},
        ]
        return context


class RequestNotificationEditView(SquestUpdateView):
    model = RequestNotification
    form_class = RequestNotificationForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        return RequestNotification.objects.filter(profile=self.request.user.profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_header'] = 'profiles/forms/form_headers/request_notification_filter_header.html'
        context['breadcrumbs'] = [
            {'text': 'Profile', 'url': reverse_lazy('profiles:profile') + '#request-notifications'},
            {'text': self.get_object(), 'url': self.get_object().get_absolute_url()},
            {'text': 'Edit', 'url': ""},
        ]
        return context
