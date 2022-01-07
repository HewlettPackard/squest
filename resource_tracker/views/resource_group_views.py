from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from guardian.mixins import LoginRequiredMixin

from resource_tracker.filters.resource_group_filter import ResourceGroupFilter
from resource_tracker.forms import ResourceGroupForm
from resource_tracker.models import ResourceGroup
from resource_tracker.tables.resource_group_table import ResourceGroupTable


@method_decorator(login_required, name='dispatch')
class ResourceGroupListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = ResourceGroupTable
    model = ResourceGroup
    template_name = 'generics/list.html'
    filterset_class = ResourceGroupFilter

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied
        return super(ResourceGroupListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Resource groups"
        context['app_name'] = "resource_tracker"
        context['object_name'] = "resource_group"
        context['html_button_path'] = "generics/buttons/generic_add_button.html"
        return context


@user_passes_test(lambda u: u.is_superuser)
def resource_group_edit(request, resource_group_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    form = ResourceGroupForm(request.POST or None, instance=resource_group)
    if form.is_valid():
        form.save()
        return redirect("resource_tracker:resource_group_list")
    breadcrumbs = [
        {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
        {'text': resource_group.name, 'url': ""},
    ]
    context = {'form': form, 'resource_group': resource_group, 'breadcrumbs': breadcrumbs, 'action': 'edit'}
    return render(request,
                  'resource_tracking/resource_group/resource-group-edit.html', context)


@user_passes_test(lambda u: u.is_superuser)
def resource_group_create(request):
    if request.method == 'POST':
        form = ResourceGroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("resource_tracker:resource_group_list")
    else:
        form = ResourceGroupForm()
    breadcrumbs = [
        {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
        {'text': 'Create a new resource group', 'url': ""},
    ]
    context = {'form': form, 'breadcrumbs': breadcrumbs, 'action': 'create'}
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def resource_group_delete(request, resource_group_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    if request.method == 'POST':
        # delete all resource attributes
        resource_group.resources.all().delete()
        resource_group.attribute_definitions.all().delete()
        resource_group.text_attribute_definitions.all().delete()
        resource_group.delete()
        # delete all resources
        return redirect("resource_tracker:resource_group_list")
    breadcrumbs = [
        {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
        {'text': resource_group.name, 'url': ""},
    ]
    context = {'resource_group': resource_group, 'breadcrumbs': breadcrumbs}
    return render(request,
                  'resource_tracking/resource_group/resource-group-delete.html', context)
