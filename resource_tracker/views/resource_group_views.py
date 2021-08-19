from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from resource_tracker.filtersets import ResourceGroupFilter
from resource_tracker.forms import ResourceGroupForm
from resource_tracker.models import ResourceGroup


@user_passes_test(lambda u: u.is_superuser)
def resource_group_list(request):
    resource_group_list = ResourceGroup.objects.all()
    resource_group_filtered = ResourceGroupFilter(request.GET, queryset=resource_group_list)
    return render(request, 'resource_tracking/resource_group/resource-group-list.html',
                  {'resource_groups': resource_group_filtered})


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
    return render(request, 'resource_tracking/resource_group/resource-group-create.html', context)


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
