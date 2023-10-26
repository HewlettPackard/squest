from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from Squest.utils.squest_table import SquestRequestConfig

from profiles.models import Token
from profiles.tables import RequestNotificationFilterTable, InstanceNotificationFilterTable


@login_required
def profile(request):
    tokens = Token.objects.filter(user=request.user)
    config = SquestRequestConfig(request)
    context = dict()
    context['tokens'] = tokens
    context['title'] = 'Profile'
    context['request_filter_table'] = RequestNotificationFilterTable(
        request.user.profile.request_notification_filters.all(), prefix="instance-")
    config.configure(context['request_filter_table'])
    context['instance_filter_table'] = InstanceNotificationFilterTable(
        request.user.profile.instance_notification_filters.all(), prefix="request-")
    config.configure(context['instance_filter_table'])
    context['app_name'] = 'profiles'

    return render(request, 'profiles/profile.html', context)


@login_required
def dark_light_theme_switch(request):
    if request.user.profile.theme == "dark":
        request.user.profile.theme = "light"
    else:
        request.user.profile.theme = "dark"
    request.user.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
