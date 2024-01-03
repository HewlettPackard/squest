from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from jinja2 import UndefinedError

from Squest.utils.squest_views import SquestListView
from service_catalog.filters.doc_filter import DocFilter
from service_catalog.models import Doc, Instance
from service_catalog.tables.doc_tables import DocTable

import logging

logger = logging.getLogger(__name__)


class DocListView(SquestListView):
    table_class = DocTable
    model = Doc
    filterset_class = DocFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['html_button_path'] = ""
        context['extra_html_button_path'] = "service_catalog/buttons/manage_docs.html"
        return context


@login_required
def doc_details(request, pk, instance_id=None):
    doc = get_object_or_404(Doc, id=pk)
    if not request.user.has_perm('service_catalog.view_doc', doc):
        raise PermissionDenied

    rendered_doc = doc.content

    if instance_id is not None:
        instance = get_object_or_404(Instance, id=instance_id)
        if not request.user.has_perm('service_catalog.view_instance', instance):
            raise PermissionDenied
        try:
            rendered_doc = doc.render(instance)
        except UndefinedError as e:
            logger.warning(f"Error: {e.message}, instance: {instance}, doc: {doc}")
            messages.warning(request, f'Failure while templating documentations: {e.message}')
        breadcrumbs = [
            {'text': 'Instances', 'url': reverse('service_catalog:instance_list')},
            {'text': f"{instance}", 'url': instance.get_absolute_url()},
            {'text': "Documentation", 'url': ""},
            {'text': doc.title, 'url': ""}
        ]
    else:
        breadcrumbs = [
            {'text': 'Documentations', 'url': reverse('service_catalog:doc_list')},
            {'text': doc.title, 'url': ""}
        ]

    context = {
        "doc": doc,
        "rendered_doc": rendered_doc,
        "breadcrumbs": breadcrumbs
    }
    return render(request,
                  'service_catalog/common/documentation/doc-show.html', context)
