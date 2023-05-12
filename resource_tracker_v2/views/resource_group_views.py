from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from resource_tracker_v2.filters.resource_group_filter import ResourceGroupFilter
from resource_tracker_v2.forms.resource_group_form import ResourceGroupForm
from resource_tracker_v2.models import ResourceGroup
from resource_tracker_v2.tables.resource_group_table import ResourceGroupTable


class ResourceGroupListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_class = ResourceGroupTable
    model = ResourceGroup
    filterset_class = ResourceGroupFilter
    template_name = 'generics/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Resource group"
        context['app_name'] = "resource_tracker"
        context['object_name'] = "resource_group"
        context['html_button_path'] = "generics/buttons/generic_add_button.html"
        return context


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
        {'text': 'Resource group', 'url': reverse('resource_tracker:resource_group_list')},
        {'text': 'Create a new resource group', 'url': ""},
    ]
    context = {'form': form, 'breadcrumbs': breadcrumbs, 'action': 'create'}
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def resource_group_edit(request, resource_group_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    form = ResourceGroupForm(request.POST or None, instance=resource_group)
    if form.is_valid():
        form.save()
        return redirect("resource_tracker:resource_group_list")
    breadcrumbs = [
        {'text': 'Resource group', 'url': reverse('resource_tracker:resource_group_list')},
        {'text': resource_group.name, 'url': ""},
    ]
    context = {'form': form, 'breadcrumbs': breadcrumbs, 'action': 'edit'}
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def resource_group_delete(request, resource_group_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    if request.method == 'POST':
        resource_group.delete()
        return redirect("resource_tracker:resource_group_list")
    breadcrumbs = [
        {'text': 'Attribute definition', 'url': reverse('resource_tracker:resource_group_list')},
        {'text': resource_group.name, 'url': ""},
    ]
    context = {'resource_group': resource_group, 'breadcrumbs': breadcrumbs}
    return render(request,
                  'resource_tracking_v2/resource_group/resource-group-delete.html', context)
