from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from profiles.models import Token
from profiles.tables.notification_filter_table import NotificationFilterTable


@login_required
def profile(request):
    tokens = Token.objects.filter(user=request.user)
    context = {
        'tokens': tokens,
        'title': 'Profile',
        'table': NotificationFilterTable(request.user.profile.notification_filters.all()),
        'app_name': 'profiles',
        'object_name': 'notification_filter'
    }
    return render(request, 'profiles/profile.html', context)
