from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, QuerySet, F
from django.utils import timezone
from django.shortcuts import render
from guardian.shortcuts import get_objects_for_user

from service_catalog.models.announcement import Announcement
from service_catalog.models.instance import InstanceState
from service_catalog.models.request import RequestState
from service_catalog.models import Request, Instance, Support, Service
from service_catalog.models.squest_settings import SquestSettings
from service_catalog.models.support import SupportState


@login_required
def home(request):
    context = dict()
    now = timezone.now()
    context['announcements'] = Announcement.objects.filter(date_start__lte=now).filter(date_stop__gte=now)
    context['squest_settings'] = SquestSettings.load()
    if request.user.is_superuser:
        context['total_request'] = Request.objects.filter(state=RequestState.SUBMITTED).count()
        context['total_instance'] = Instance.objects.filter(state='AVAILABLE').count()
        context['total_support_opened'] = Support.objects.filter(state='OPENED').count()
        context['total_user_without_billing_groups'] = User.objects.filter(billing_groups=None).count()
        context['total_user'] = User.objects.all().count()

        # Create a dict that represent {service, number_of_instance, submitted_request}
        all_services = Service.objects.all()
        instances = Instance.objects.filter(state=InstanceState.AVAILABLE).values('service')\
            .annotate(service_name=F('service__name'))\
            .annotate(instance_count=Count('service_name'))\
            .order_by('service_name')
        submitted_requests = Request.objects.filter(state=RequestState.SUBMITTED).values('instance__service__name')\
            .annotate(service_name=F('instance__service__name'))\
            .annotate(request_count=Count('service_name'))\
            .order_by('service_name')
        failed_requests = Request.objects.filter(state=RequestState.FAILED).values('instance__service__name') \
            .annotate(service_name=F('instance__service__name')) \
            .annotate(request_count=Count('service_name')) \
            .order_by('service_name')
        opened_supports = Support.objects.filter(state=SupportState.OPENED).values('instance__service__name') \
            .annotate(service_name=F('instance__service__name')) \
            .annotate(request_count=Count('service_name')) \
            .order_by('service_name')

        service_details = dict()
        for service in all_services:
            service_details[service.name] = {
                "service": service,
                "instances": 0,
                "submitted_request": 0,
                "failed_requests": 0,
                "opened_supports": 0,
            }
            if instances.filter(service=service.id).exists():
                service_details[service.name]["instances"] = instances.get(service=service.id)["instance_count"]
            if submitted_requests.filter(instance__service=service.id).exists():
                service_details[service.name]["submitted_request"] = submitted_requests.get(instance__service=service.id)["request_count"]
            if failed_requests.filter(instance__service=service.id).exists():
                service_details[service.name]["failed_requests"] = failed_requests.get(instance__service=service.id)["request_count"]
            if opened_supports.filter(instance__service=service.id).exists():
                service_details[service.name]["opened_supports"] = opened_supports.get(instance__service=service.id)["request_count"]

        context["service_details"] = service_details

    else:
        context['total_request'] = get_objects_for_user(request.user, 'service_catalog.view_request').filter(
                state=RequestState.SUBMITTED).count()
        context['total_request_need_info'] = get_objects_for_user(request.user, 'service_catalog.view_request').filter(
            state=RequestState.NEED_INFO).count()
        context['total_instance'] = get_objects_for_user(request.user, 'service_catalog.view_instance').filter(
                state=InstanceState.AVAILABLE).count()
    return render(request, 'home/home.html', context=context)
