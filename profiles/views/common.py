from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from profiles.models import Token
from profiles.tables.notification_filter_table import RequestNotificationFilterTable, \
    SupportNotificationFilterTable


@login_required
def profile(request):
    tokens = Token.objects.filter(user=request.user)
    context = {
        'tokens': tokens,
        'title': 'Profile',
        'request_filter_table': RequestNotificationFilterTable(request.user.profile.request_notification_filters.all()),
        'support_filter_table': SupportNotificationFilterTable(request.user.profile.instance_notification_filters.all()),
        'app_name': 'profiles',
    }
    return render(request, 'profiles/profile.html', context)
