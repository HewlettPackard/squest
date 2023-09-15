from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
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

    all_supports = Support.get_queryset_for_user(request.user, 'service_catalog.view_support') \
        .values('instance__service', 'state') \
        .annotate(count=Count('id', distinct=True)) \
        .order_by('instance__service')

    all_instances = Instance.get_queryset_for_user(request.user, 'service_catalog.view_instance') \
        .values('service', 'state') \
        .annotate(count=Count('id', distinct=True)) \
        .order_by('service')

    all_requests = Request.get_queryset_for_user(request.user, 'service_catalog.view_request') \
        .values('instance__service', 'state') \
        .annotate(count=Count('id', distinct=True)) \
        .order_by('instance__service')

    if request.user.has_perm('service_catalog.list_request'):
        context['total_request'] = sum([x["count"] for x in all_requests if x["state"] == RequestState.SUBMITTED])
        context['total_request_need_info'] = sum(
            [x["count"] for x in all_requests if x["state"] == RequestState.NEED_INFO])

    if request.user.has_perm('service_catalog.list_instance'):
        context['total_instance'] = sum([x["count"] for x in all_instances if x["state"] == InstanceState.AVAILABLE])

    if request.user.has_perm('service_catalog.list_support'):
        context['total_support_opened'] = sum([x["count"] for x in all_supports if x["state"] == SupportState.OPENED])

    if request.user.has_perm('auth.list_user'):
        context['total_user'] = User.objects.all().count()
        context['user_without_organization'] = User.objects.filter(groups__isnull=True).count()

    if request.user.has_perm('service_catalog.list_service'):
        all_services = Service.get_queryset_for_user(request.user, 'service_catalog.view_service').filter(enabled=True)
        service_details = dict()
        for service in all_services:
            service_dict = dict()
            service_dict["instances"] = sum([x["count"] for x in all_instances if
                                             x["state"] == InstanceState.AVAILABLE and x["service"] == service.id])

            service_dict["accepted_requests"] = sum([x["count"] for x in all_requests if
                                                     x["state"] == RequestState.ACCEPTED and x[
                                                         "instance__service"] == service.id])

            service_dict["submitted_requests"] = sum([x["count"] for x in all_requests if
                                                      x["state"] == RequestState.SUBMITTED and x[
                                                          "instance__service"] == service.id])

            service_dict["failed_requests"] = sum([x["count"] for x in all_requests if
                                                   x["state"] == RequestState.FAILED and x[
                                                       "instance__service"] == service.id])

            service_dict["need_info_requests"] = sum([x["count"] for x in all_requests if
                                                      x["state"] == RequestState.NEED_INFO and x[
                                                          "instance__service"] == service.id])

            service_dict["opened_supports"] = sum([x["count"] for x in all_supports if
                                                   x["state"] == SupportState.OPENED and x[
                                                       "instance__service"] == service.id])

            if sum([v for v in service_dict.values()]) > 0:
                service_dict["service"] = service
                service_details[service.name] = service_dict

        if service_details:
            context["service_details"] = service_details

    return render(request, 'home/home.html', context=context)
