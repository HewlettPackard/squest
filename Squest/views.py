from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, F
from django.utils import timezone
from django.shortcuts import render

from service_catalog.models.announcement import Announcement
from service_catalog.models.instance import InstanceState
from service_catalog.models.request import RequestState
from service_catalog.models import Request, Instance, Support, Service
from service_catalog.models.support import SupportState


@login_required
def home(request):
    context = dict()
    now = timezone.now()
    context['announcements'] = Announcement.objects.filter(date_start__lte=now).filter(date_stop__gte=now)

    all_instances = Instance.get_queryset_for_user(request.user, 'service_catalog.view_instance')
    all_requests = Request.get_queryset_for_user(request.user, 'service_catalog.view_request')
    all_supports = Support.get_queryset_for_user(request.user, 'service_catalog.view_support')
    if request.user.has_perm('service_catalog.list_request'):
        context['total_request'] = all_requests.filter(state=RequestState.SUBMITTED).count()
        context['total_request_need_info'] = all_requests.filter(state=RequestState.NEED_INFO).count()

    if request.user.has_perm('service_catalog.list_instance'):
        context['total_instance'] = all_instances.filter(state='AVAILABLE').count()

    if request.user.has_perm('service_catalog.list_support'):
        context['total_support_opened'] = all_supports.filter(state='OPENED').count()

    if request.user.has_perm('auth.list_user'):
        context['total_user'] = User.objects.all().count()

    if request.user.has_perm('service_catalog.list_service'):
        # Create a dict that represent {service, number_of_instance, submitted_request}
        all_services = Service.get_queryset_for_user(request.user, 'service_catalog.view_service').filter(enabled=True)
        instances = all_instances.filter(state=InstanceState.AVAILABLE).values('service') \
            .annotate(service_name=F('service__name')) \
            .annotate(instance_count=Count('service_name')) \
            .order_by('service_name')
        accepted_requests = all_requests.filter(state__in=[RequestState.ACCEPTED]) \
            .values('instance__service__name') \
            .annotate(service_name=F('instance__service__name')) \
            .annotate(request_count=Count('service_name')) \
            .order_by('service_name')
        submitted_requests = all_requests.filter(state__in=[RequestState.SUBMITTED]) \
            .values('instance__service__name') \
            .annotate(service_name=F('instance__service__name')) \
            .annotate(request_count=Count('service_name')) \
            .order_by('service_name')
        failed_requests = all_requests.filter(state=RequestState.FAILED).values('instance__service__name') \
            .annotate(service_name=F('instance__service__name')) \
            .annotate(request_count=Count('service_name')) \
            .order_by('service_name')
        need_info_requests = all_requests.filter(state=RequestState.NEED_INFO).values('instance__service__name') \
            .annotate(service_name=F('instance__service__name')) \
            .annotate(request_count=Count('service_name')) \
            .order_by('service_name')
        if request.user.has_perm('service_catalog.list_support'):
            opened_supports = all_supports.filter(state=SupportState.OPENED).values('instance__service__name') \
                .annotate(service_name=F('instance__service__name')) \
                .annotate(request_count=Count('service_name')) \
                .order_by('service_name')
        else:
            opened_supports = Support.objects.none()


        service_details = dict()
        for service in all_services:
            service_details[service.name] = {
                "service": service,
                "instances": 0
            }
            if instances.filter(service=service.id).exists():
                service_details[service.name]["instances"] = instances.get(service=service.id)["instance_count"]
            if accepted_requests.filter(instance__service=service.id).exists():
                service_details[service.name]["accepted_requests"] = accepted_requests.get(instance__service=service.id)[
                    "request_count"]
            if submitted_requests.filter(instance__service=service.id).exists():
                service_details[service.name]["submitted_requests"] = \
                submitted_requests.get(instance__service=service.id)["request_count"]
            if failed_requests.filter(instance__service=service.id).exists():
                service_details[service.name]["failed_requests"] = failed_requests.get(instance__service=service.id)[
                    "request_count"]
            if need_info_requests.filter(instance__service=service.id).exists():
                service_details[service.name]["need_info_requests"] = \
                need_info_requests.get(instance__service=service.id)["request_count"]
            if opened_supports.filter(instance__service=service.id).exists():
                service_details[service.name]["opened_supports"] = opened_supports.get(instance__service=service.id)[
                    "request_count"]

        context["service_details"] = service_details
        context['user_without_organization'] = User.objects.filter(groups__isnull=True).count()

    return render(request, 'home/home.html', context=context)
