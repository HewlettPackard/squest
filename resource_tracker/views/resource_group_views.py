from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe

from resource_tracker.filtersets import ResourceGroupFilter
from resource_tracker.forms import ResourceGroupForm
from resource_tracker.models import ResourceGroup


@user_passes_test(lambda u: u.is_superuser)
def resource_group_list(request):
    resource_group_list = ResourceGroup.objects.all()
    resource_group_filtered = ResourceGroupFilter(request.GET, queryset=resource_group_list)
    breadcrumbs = [
        {'text': 'Resource groups', 'url': ''},
    ]
    context = {'breadcrumbs': breadcrumbs, "resource_groups": resource_group_filtered}
    return render(request, 'resource_tracking/resource_group/resource-group-list.html', context=context)


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
    template = {'form': {'button': 'edit'}}
    context = {'form': form, 'resource_group': resource_group, 'breadcrumbs': breadcrumbs, 'template': template}
    return render(request, 'resource_tracking/resource_group/resource-group-edit.html', context)


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
    template = {'form': {'button': 'create'}}
    context = {'form': form, 'breadcrumbs': breadcrumbs, 'template': template}
    return render(request, 'generics/create_page.html', context)


@user_passes_test(lambda u: u.is_superuser)
def resource_group_delete(request, resource_group_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    if request.method == 'POST':
        # delete all resource attributes
        resource_group.resources.all().delete()
        resource_group.attribute_definitions.all().delete()
        resource_group.delete()
        # delete all resources
        return redirect("resource_tracker:resource_group_list")
    breadcrumbs = [
        {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
        {'text': resource_group.name, 'url': ""},
    ]
    if resource_group.resources.all():
        details = {
            'warning_sentence': 'The deletion of this resource group will drive to the deletion of the following resources:',
            'details_list': [resource.name for resource in resource_group.resources.all()]
        }
    else:
        details = {
            'warning_sentence': 'No resources present in the resource group. Can be safely deleted.'

        }
    template_form = {
        'confirm_text': mark_safe(f"Confirm deletion of the resource group <strong>{resource_group.name}</strong>"),
        'button_text': 'Delete',
        'details': details
    }
    context = {'resource_group': resource_group, 'breadcrumbs': breadcrumbs, 'template_form': template_form}
    return render(request, 'generics/confirm-delete-template.html', context=context)
