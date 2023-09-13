from Squest.utils.squest_views import *
from service_catalog.filters.global_hook_filter import InstanceHookFilter, RequestHookFilter
from service_catalog.forms import InstanceHookForm, RequestHookForm
from service_catalog.models import InstanceHook, RequestHook

from service_catalog.tables.global_hook_tables import InstanceHookTable, RequestHookTable


class InstanceHookListView(SquestListView):
    model = InstanceHook
    filterset_class = InstanceHookFilter
    table_class = InstanceHookTable


class InstanceHookCreateView(SquestCreateView):
    model = InstanceHook
    form_class = InstanceHookForm


class InstanceHookEditView(SquestUpdateView):
    model = InstanceHook
    form_class = InstanceHookForm


class InstanceHookDeleteView(SquestDeleteView):
    model = InstanceHook


class RequestHookListView(SquestListView):
    model = RequestHook
    filterset_class = RequestHookFilter
    table_class = RequestHookTable


class RequestHookCreateView(SquestCreateView):
    model = RequestHook
    form_class = RequestHookForm


class RequestHookEditView(SquestUpdateView):
    model = RequestHook
    form_class = RequestHookForm


class RequestHookDeleteView(SquestDeleteView):
    model = RequestHook
