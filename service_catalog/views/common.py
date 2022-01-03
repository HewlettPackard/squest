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

from service_catalog.models import Doc
from service_catalog.models import Request, Instance, Support, Service
from service_catalog.models.announcement import Announcement
from service_catalog.models.instance import InstanceState
from service_catalog.models.request import RequestState
from .color import random_color


def get_color_from_string(string):
    return list(random_color.values())[hash(string) % len(random_color)]


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
