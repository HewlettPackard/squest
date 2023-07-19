from django.urls import reverse
from Squest.utils.squest_views import *
from resource_tracker_v2.filters.resource_group_filter import ResourceGroupFilter
from resource_tracker_v2.forms.resource_group_form import ResourceGroupForm
from resource_tracker_v2.models import ResourceGroup
from resource_tracker_v2.tables.resource_group_table import ResourceGroupTable


class ResourceGroupListView(SquestListView):
    model = ResourceGroup
    filterset_class = ResourceGroupFilter
    table_class = ResourceGroupTable


class ResourceGroupCreateView(SquestCreateView):
    model = ResourceGroup
    form_class = ResourceGroupForm


class ResourceGroupEditView(SquestUpdateView):
    model = ResourceGroup
    form_class = ResourceGroupForm
    pk_url_kwarg = "resource_group_id"


class ResourceGroupDeleteView(SquestDeleteView):
    model = ResourceGroup
    pk_url_kwarg = "resource_group_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['details'] = {
            'warning_sentence': 'Warning: This resource group is in use by following resource:',
            'details_list': [f"{resource}," for resource in self.get_object().resources.all()]
        }
        return context