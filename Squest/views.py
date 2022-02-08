from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import render
from guardian.shortcuts import get_objects_for_user
from service_catalog.models.announcement import Announcement
from service_catalog.models.instance import InstanceState
from service_catalog.models.request import RequestState
from service_catalog.models import Request, Instance, Support


@login_required
def home(request):
    context = dict()
    now = timezone.now()
    context['announcements'] = Announcement.objects.filter(date_start__lte=now).filter(date_stop__gte=now)
    if request.user.is_superuser:
        context['total_request'] = Request.objects.filter(state=RequestState.SUBMITTED).count()
        context['total_instance'] = Instance.objects.filter(state='AVAILABLE').count()
        context['total_support_opened'] = Support.objects.filter(state='OPENED').count()
        context['total_user_without_billing_groups'] = User.objects.filter(billing_groups=None).count()
        context['total_user'] = User.objects.all().count()
    else:
        context['total_request'] = get_objects_for_user(request.user, 'service_catalog.view_request').filter(
                state=RequestState.SUBMITTED).count()
        context['total_request_need_info'] = get_objects_for_user(request.user, 'service_catalog.view_request').filter(
            state=RequestState.NEED_INFO).count()
        context['total_instance'] = get_objects_for_user(request.user, 'service_catalog.view_instance').filter(
                state=InstanceState.AVAILABLE).count()
    return render(request, 'home/home.html', context=context)
