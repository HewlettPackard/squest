from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe

from resource_tracker.forms import ResourceForm
from resource_tracker.models import ResourceGroup, Resource


@user_passes_test(lambda u: u.is_superuser)
def resource_group_resource_bulk_delete_confirm(request, resource_group_id):
    if request.method == "POST":
        pks = request.POST.getlist("selection")
        selected_resources = Resource.objects.filter(pk__in=pks)
        args = {
            "resource_group_id": resource_group_id
        }
        breadcrumbs = [
            {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
            {'text': 'Resources', 'url': reverse('resource_tracker:resource_group_resource_list', kwargs={'resource_group_id': resource_group_id})},
            {'text': "Delete multiple", 'url': ""}
        ]
        context = {
            'breadcrumbs': breadcrumbs,
            'confirm_text': mark_safe(f"Confirm deletion of the following resources?"),
            'action_url': reverse('resource_tracker:resource_group_resource_bulk_delete', kwargs=args),
            'object_list': selected_resources,
            'button_text': 'Delete',
        }
        return render(request, 'generics/confirm-bulk-delete-template.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def resource_group_resource_bulk_delete(request, resource_group_id):
    if request.method == "POST":
        pks = request.POST.getlist("selection")
        selected_resources = Resource.objects.filter(pk__in=pks)
        selected_resources.delete()
    return redirect("resource_tracker:resource_group_resource_list", resource_group_id)


@user_passes_test(lambda u: u.is_superuser)
def resource_group_resource_delete(request, resource_group_id, resource_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    resource = get_object_or_404(Resource, id=resource_id)
    if request.method == "POST":
        resource.delete()
        return redirect("resource_tracker:resource_group_resource_list", resource_group_id)
    breadcrumbs = [
        {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
        {'text': resource_group.name,
         'url': reverse('resource_tracker:resource_group_resource_list', args=[resource_group_id])},
        {'text': resource.name, 'url': ""},
    ]
    context = {
        "resource_group": resource_group,
        "resource": resource,
        'breadcrumbs': breadcrumbs
    }
    return render(request, "resource_tracking/resource_group/resources/resource-delete.html", context)


@user_passes_test(lambda u: u.is_superuser)
def resource_group_resource_create(request, resource_group_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    parameters = {
        "resource_group_id": resource_group.id
    }
    if request.method == 'POST':
        form = ResourceForm(request.POST, **parameters)
        if form.is_valid():
            form.save()
            return redirect("resource_tracker:resource_group_resource_list", resource_group.id)
    else:
        form = ResourceForm(**parameters)
    breadcrumbs = [
        {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
        {'text': resource_group.name,
         'url': reverse('resource_tracker:resource_group_resource_list', args=[resource_group_id])},
        {'text': 'Create a new resource', 'url': ""},
    ]
    context = {'resource_group': resource_group, 'form': form, 'breadcrumbs': breadcrumbs, 'action': 'create'}
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def resource_group_resource_edit(request, resource_group_id, resource_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    resource = get_object_or_404(Resource, id=resource_id)
    parameters = {
        "resource_group_id": resource_group.id
    }
    if request.method == 'POST':
        form = ResourceForm(request.POST, instance=resource, **parameters)
        if form.is_valid():
            form.save()
            return redirect("resource_tracker:resource_group_resource_list", resource_group.id)
    else:
        form = ResourceForm(instance=resource, **parameters)
    breadcrumbs = [
        {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
        {'text': resource_group.name,
         'url': reverse('resource_tracker:resource_group_resource_list', args=[resource_group_id])},
        {'text': resource.name, 'url': ""},
    ]
    context = {'resource_group': resource_group, 'resource': resource, 'form': form, 'breadcrumbs': breadcrumbs,
               'action': 'edit'}
    return render(request, 'generics/generic_form.html', context)
