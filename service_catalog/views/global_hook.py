from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from Squest.utils.squest_views import *
from service_catalog.filters.global_hook_filter import GlobalHookFilter
from service_catalog.forms import GlobalHookForm
from service_catalog.models import GlobalHook
from service_catalog.models.instance import InstanceState
from service_catalog.models.request import RequestState
from service_catalog.models.services import Service
from service_catalog.tables.global_hook_tables import GlobalHookTable


class GlobalHookListView(SquestListView):
    model = GlobalHook
    filterset_class = GlobalHookFilter
    table_class = GlobalHookTable


class GlobalHookCreateView(SquestCreateView):
    model = GlobalHook
    form_class = GlobalHookForm
    template_name = "service_catalog/settings/global_hooks/global-hook-create.html"

class GlobalHookEditView(SquestUpdateView):
    model = GlobalHook
    form_class = GlobalHookForm
    template_name = "service_catalog/settings/global_hooks/global-hook-edit.html"


class GlobalHookDeleteView(SquestDeleteView):
    model = GlobalHook


@login_required
def ajax_load_model_state(request):
    if not request.user.has_perm('service_catalog.change_globalhook') and not request.user.has_perm(
            'service_catalog.add_globalhook'):
        raise PermissionDenied
    model = request.GET.get('model')
    options = [('', '----------')]
    if model == "Instance":
        options = InstanceState.choices
    if model == "Request":
        options = RequestState.choices
    return render(request, 'service_catalog/settings/global_hooks/state-dropdown-list-option.html',
                  {'options': options})


@login_required
def ajax_load_service_operations(request):
    if not request.user.has_perm('service_catalog.change_globalhook') and not request.user.has_perm(
            'service_catalog.add_globalhook'):
        raise PermissionDenied
    service_id = int(request.GET.get('service'))
    options = [('', '----------')]
    if service_id != 0:
        services = Service.objects.filter(id=service_id)
        if services.count() == 1:
            options = [(operation.id, operation.name) for operation in services[0].operations.all()]
    return render(request, 'service_catalog/settings/global_hooks/state-dropdown-list-option.html',
                  {'options': options})
