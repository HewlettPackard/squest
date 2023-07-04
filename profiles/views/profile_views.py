from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect


@login_required
def dark_light_theme_switch(request):
    if request.user.profile.theme == "dark":
        request.user.profile.theme = "light"
    else:
        request.user.profile.theme = "dark"
    request.user.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
