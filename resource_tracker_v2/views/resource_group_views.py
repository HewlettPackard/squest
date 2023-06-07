from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from resource_tracker_v2.filters.resource_group_filter import ResourceGroupFilter
from resource_tracker_v2.forms.resource_group_form import ResourceGroupForm
from resource_tracker_v2.models import ResourceGroup
from resource_tracker_v2.tables.resource_group_table import ResourceGroupTable


class ResourceGroupListView(PermissionRequiredMixin, SingleTableMixin, FilterView):
    table_class = ResourceGroupTable
    model = ResourceGroup
    filterset_class = ResourceGroupFilter
    template_name = 'generics/list.html'
    permission_required = "is_superuser"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Resource group"
        context['app_name'] = "resource_tracker"
        context['object_name'] = "resource_group"
        context['html_button_path'] = "generics/buttons/generic_add_button.html"
        return context


class ResourceGroupCreateView(PermissionRequiredMixin, CreateView):
    model = ResourceGroup
    template_name = 'generics/generic_form.html'
    form_class = ResourceGroupForm
    permission_required = "is_superuser"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Resource group"
        context['app_name'] = "resource_tracker"
        context['object_name'] = "resource_group"
        context['action'] = "create"
        context[""] = [
            {'text': 'Resource group', 'url': reverse('resource_tracker:resource_group_list')},
            {'text': 'Create a new resource group', 'url': ""},
        ]
        return context


class ResourceGroupEditView(PermissionRequiredMixin, UpdateView):
    model = ResourceGroup
    template_name = 'generics/generic_form.html'
    form_class = ResourceGroupForm
    permission_required = "is_superuser"
    pk_url_kwarg = "resource_group_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Resource group"
        context['app_name'] = "resource_tracker"
        context['object_name'] = "resource_group"
        context['action'] = "edit"
        context[""] = [
            {'text': 'Resource group', 'url': reverse('resource_tracker:resource_group_list')},
            {'text': self.object.name, 'url': ""},
        ]
        return context


class ResourceGroupDeleteView(PermissionRequiredMixin, DeleteView):
    model = ResourceGroup
    template_name = 'resource_tracking_v2/resource_group/resource-group-delete.html'
    success_url = reverse_lazy("resource_tracker:resource_group_list")
    permission_required = "is_superuser"
    pk_url_kwarg = "resource_group_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        breadcrumbs = [
            {'text': 'Resource group', 'url': reverse('resource_tracker:resource_group_list')},
            {'text': self.object.name, 'url': ""},
        ]
        context['breadcrumbs'] = breadcrumbs
        return context
