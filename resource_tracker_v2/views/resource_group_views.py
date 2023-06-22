from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView


from Squest.utils.squest_views import SquestListView
from resource_tracker_v2.filters.resource_group_filter import ResourceGroupFilter
from resource_tracker_v2.forms.resource_group_form import ResourceGroupForm
from resource_tracker_v2.models import ResourceGroup
from resource_tracker_v2.tables.resource_group_table import ResourceGroupTable


class ResourceGroupListView(PermissionRequiredMixin, SquestListView):
    table_class = ResourceGroupTable
    model = ResourceGroup
    filterset_class = ResourceGroupFilter
    template_name = 'generics/list.html'
    permission_required = "is_superuser"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['html_button_path'] = "generics/buttons/generic_add_button.html"
        return context


class ResourceGroupCreateView(PermissionRequiredMixin, CreateView):
    model = ResourceGroup
    template_name = 'generics/generic_form.html'
    form_class = ResourceGroupForm
    permission_required = "is_superuser"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        content_type = ContentType.objects.get_for_model(self.model)

        context['title'] = f'Create {content_type.name}'
        context['app_name'] = content_type.app_label
        context['object_name'] = content_type.model
        context['action'] = "create"
        context["breadcrumbs"] = [
            {'text': content_type.name.capitalize(), 'url': reverse(f'{content_type.app_label}:{content_type.model}_list')},
            {'text': f'Create a new {content_type.name}', 'url': ""},
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

        content_type = ContentType.objects.get_for_model(self.model)

        context['title'] = f'Edit {content_type.name}'
        context['app_name'] = content_type.app_label
        context['object_name'] = content_type.model
        context['action'] = "edit"
        context["breadcrumbs"] = [
            {'text': 'Resource group', 'url': reverse('resource_tracker_v2:resourcegroup_list')},
            {'text': self.object.name, 'url': ""},
        ]
        return context


class ResourceGroupDeleteView(PermissionRequiredMixin, DeleteView):
    model = ResourceGroup
    template_name = 'resource_tracking_v2/resource_group/resource-group-delete.html'
    success_url = reverse_lazy("resource_tracker_v2:resourcegroup_list")
    permission_required = "is_superuser"
    pk_url_kwarg = "resource_group_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        breadcrumbs = [
            {'text': 'Resource group', 'url': reverse('resource_tracker_v2:resourcegroup_list')},
            {'text': self.object.name, 'url': ""},
        ]
        context['breadcrumbs'] = breadcrumbs
        return context
