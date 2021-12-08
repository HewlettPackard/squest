import json
import os
import uuid
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from guardian.shortcuts import get_objects_for_user
from martor.utils import LazyEncoder
from profiles.models import BillingGroup
from resource_tracker.models import ResourcePool
from service_catalog.models import Doc
from service_catalog.models import Request, Instance, Support, Service
from service_catalog.models.announcement import Announcement
from service_catalog.models.instance import InstanceState
from service_catalog.models.request import RequestState
from .color import map_dict_request_state, random_color, map_class_to_color


def get_color_from_string(string):
    return list(random_color.values())[hash(string) % len(random_color)]


def create_pie_chart_request_by_state() -> dict:
    pie_chart_state = {
        'title': 'Request by state',
        'id': 'pie-chart-state',
        'data':
            {
                'labels': [],
                'datasets':
                    [
                        {
                            'data': [],
                            'backgroundColor': [],
                        }
                    ]
            }

    }
    pie_chart_state_tmp = dict()
    queryset = Request.objects.filter()
    for squest_request in queryset:
        pie_chart_state_tmp[squest_request.state] = pie_chart_state_tmp.get(squest_request.state, 0) + 1
    path = pie_chart_state['data']
    for state, count in pie_chart_state_tmp.items():
        path['labels'].append(state)
        path['datasets'][0]['data'].append(count)
        color = map_class_to_color.get(map_dict_request_state.get(state))
        path['datasets'][0]['backgroundColor'].append(color)
    return pie_chart_state


def create_pie_chart_instance_by_service_type() -> dict:
    pie_chart_service = {
        'title': 'Instance by service type',
        'id': 'pie-chart-service',
        'data':
            {
                'labels': [],
                'datasets':
                    [
                        {
                            'data': [],
                            'backgroundColor': [],
                        }
                    ]
            }

    }
    pie_chart_service_tmp = dict()
    queryset = Instance.objects.filter()
    for instance in queryset:
        key = instance.service
        pie_chart_service_tmp[key] = pie_chart_service_tmp.get(key, 0) + 1
    path = pie_chart_service['data']
    for service, count in pie_chart_service_tmp.items():
        path['labels'].append(service.name if service else "No service")
        path['datasets'][0]['data'].append(count)
        color = get_color_from_string(service.id if service else 0 + 5)  # Append X to map services on other colors than billing groups
        path['datasets'][0]['backgroundColor'].append(color)
    return pie_chart_service


def create_pie_chart_instance_by_billing_groups() -> dict:
    pie_chart_billing = {
        'title': 'Instance by billing',
        'id': 'pie-chart-instance-billing',
        'data':
            {
                'labels': [],
                'datasets':
                    [
                        {
                            'data': [],
                            'backgroundColor': [],
                        }
                    ]
            }

    }
    pie_chart_billing_tmp = dict()
    queryset = Instance.objects.filter()
    for instance in queryset:
        key = instance.billing_group
        pie_chart_billing_tmp[key] = pie_chart_billing_tmp.get(key, 0) + 1
    path = pie_chart_billing['data']
    for billing_group, count in pie_chart_billing_tmp.items():
        path['labels'].append(billing_group.name if billing_group else 'None')
        path['datasets'][0]['data'].append(count)
        color = get_color_from_string(billing_group.id if billing_group else 0)
        path['datasets'][0]['backgroundColor'].append(color)
    return pie_chart_billing


def create_pie_chart_resource_pool_consumption_by_billing_groups() -> dict:
    chart_resource_pool_tmp = dict()
    for resource_pool in ResourcePool.objects.all():
        chart_resource_pool_tmp[resource_pool] = dict()
        for rp_attribute in resource_pool.attribute_definitions.all():
            chart_resource_pool_tmp[resource_pool][rp_attribute] = dict()
            chart_resource_pool_tmp[resource_pool][rp_attribute][None] = 0

            for bg in BillingGroup.objects.all():
                chart_resource_pool_tmp[resource_pool][rp_attribute][bg] = 0
            for consumer in rp_attribute.consumers.all():
                for resource_attribute in consumer.attribute_types.all():
                    bg = None
                    if resource_attribute.resource.service_catalog_instance:
                        bg = resource_attribute.resource.service_catalog_instance.billing_group
                    chart_resource_pool_tmp[resource_pool][rp_attribute][bg] += resource_attribute.value
    chart_resource_pool = dict()
    for resource_pool in chart_resource_pool_tmp:
        chart_resource_pool[resource_pool] = dict()
        for rp_attribute in chart_resource_pool_tmp[resource_pool]:
            chart_resource_pool[resource_pool][rp_attribute] = dict()
            path = chart_resource_pool[resource_pool][rp_attribute]
            path['title'] = f"{rp_attribute}"
            path['id'] = f"pie-chart-{resource_pool.id}-{rp_attribute.id}"
            path['data'] = dict()
            path['data']['datasets'] = list()
            path['data']['labels'] = list()
            path['data']['datasets'].append(dict())
            path['data']['datasets'][0]['data'] = list()
            path['data']['datasets'][0]['backgroundColor'] = list()
            for bg in chart_resource_pool_tmp[resource_pool][rp_attribute]:
                if chart_resource_pool_tmp[resource_pool][rp_attribute][bg] == 0:
                    continue
                path['data']['labels'].append(bg.name if bg else 'None')
                path['data']['datasets'][0]['data'].append(chart_resource_pool_tmp[resource_pool][rp_attribute][bg])
                color = get_color_from_string(bg)
                path['data']['datasets'][0]['backgroundColor'].append(color)
    return chart_resource_pool


@login_required
def dashboards(request):
    context = dict()
    now = timezone.now()
    context['announcements'] = Announcement.objects.filter(date_start__lte=now).filter(date_stop__gte=now)
    context['title'] = "Dashboard"
    if request.user.is_superuser:
        context['total_request'] = Request.objects.filter(state=RequestState.SUBMITTED).count()
        context['total_instance'] = Instance.objects.filter(state='AVAILABLE').count()
        context['total_support_opened'] = Support.objects.filter(state='OPENED').count()
        context['total_user_without_billing_groups'] = User.objects.filter(billing_groups=None).count()
        context['total_user'] = User.objects.all().count()
        context['pie_charts'] = dict()
        context['pie_charts']['pie_chart_state'] = create_pie_chart_request_by_state()
        context['pie_charts']['pie_chart_service'] = create_pie_chart_instance_by_service_type()
        context['pie_charts']['pie_chart_billing'] = create_pie_chart_instance_by_billing_groups()
        context['chart_resource_pool'] = create_pie_chart_resource_pool_consumption_by_billing_groups()
    else:
        context['total_request'] = get_objects_for_user(request.user, 'service_catalog.view_request').filter(
                state=RequestState.SUBMITTED).count()
        context['total_request_need_info'] = get_objects_for_user(request.user, 'service_catalog.view_request').filter(
            state=RequestState.NEED_INFO).count()
        context['total_instance'] = get_objects_for_user(request.user, 'service_catalog.view_instance').filter(
                state=InstanceState.AVAILABLE).count()
    return render(request, 'service_catalog/common/dashboard.html', context=context)


@login_required
def service_list(request):
    services = Service.objects.filter(enabled=True)
    return render(request, 'service_catalog/common/service/service-list.html', {'services': services})


@login_required
def markdown_uploader(request):
    """
    Makdown image upload for locale storage
    and represent as json to markdown editor.
    """
    if request.method == 'POST' and request.is_ajax():
        if 'markdown-image-upload' in request.FILES:
            image = request.FILES['markdown-image-upload']
            image_types = [
                'image/png', 'image/jpg',
                'image/jpeg', 'image/pjpeg', 'image/gif'
            ]
            if image.content_type not in image_types:
                data = json.dumps({
                    'status': 405,
                    'error': _('Bad image format.')
                }, cls=LazyEncoder)
                return HttpResponse(
                    data, content_type='application/json', status=405)

            if image.size > settings.MAX_IMAGE_UPLOAD_SIZE:
                to_mb = settings.MAX_IMAGE_UPLOAD_SIZE / (1024 * 1024)
                data = json.dumps({
                    'status': 405,
                    'error': _('Maximum image file is %(size) MB.') % {'size': to_mb}
                }, cls=LazyEncoder)
                return HttpResponse(
                    data, content_type='application/json', status=405)

            img_uuid = "{0}-{1}".format(uuid.uuid4().hex[:10], image.name.replace(' ', '-'))
            tmp_file = os.path.join(settings.MARTOR_UPLOAD_PATH, img_uuid)
            def_path = default_storage.save(tmp_file, ContentFile(image.read()))
            img_url = os.path.join(settings.MEDIA_URL, def_path)

            data = json.dumps({
                'status': 200,
                'link': img_url,
                'name': image.name
            })
            return HttpResponse(data, content_type='application/json')
        return HttpResponse(_('Invalid request!'))
    return HttpResponse(_('Invalid request!'))


@login_required
def doc_show(request, doc_id):
    doc = get_object_or_404(Doc, id=doc_id)
    breadcrumbs = [
        {'text': 'Documentations', 'url': reverse('service_catalog:doc_list')},
        {'text': doc.title, 'url': ""}
    ]
    context = {
        "doc": doc,
        "breadcrumbs": breadcrumbs
    }
    return render(request,
                  'service_catalog/common/documentation/doc-show.html', context)
