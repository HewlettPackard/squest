from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe

from resource_tracker.forms import ResourceForm
from resource_tracker.models import ResourceGroup, Resource


@user_passes_test(lambda u: u.is_superuser)
def resource_group_resource_list(request, resource_group_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)

    list_attribute_name = list()
    for resource in resource_group.resources.all():
        for attribute in resource.attributes.all():
            if attribute.attribute_type.name not in list_attribute_name:
                list_attribute_name.append(attribute.attribute_type.name)
    breadcrumbs = [
        {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
        {'text': resource_group.name, 'url': ""},
    ]
    context = {
        'resource_group': resource_group,
        'list_attribute_name': list_attribute_name,
        'breadcrumbs': breadcrumbs
    }
    return render(request, 'resource_tracking/resource_group/resources/resource-list.html', context)


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

    template_form = {'confirm_text': mark_safe(f"Do you want to delete the resource: {resource.name}?"),
                     'button_text': 'Delete',
                     'details': None}
    context = {
        "resource_group": resource_group,
        "resource": resource,
        'breadcrumbs': breadcrumbs,
        'template_form': template_form
    }
    return render(request, "generics/confirm-delete-template.html", context=context)


@user_passes_test(lambda u: u.is_superuser)
def resource_group_resource_create(request, resource_group_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    parameters = {
        "resource_group_id": resource_group.id
    }
    if request.method == 'POST':
        form = ResourceForm(request.POST,  **parameters)
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
    template = {'form': {'button': 'create'}}

    context = {'resource_group': resource_group, 'form': form, 'breadcrumbs': breadcrumbs, 'template': template}
    return render(request, 'generics/create_page.html', context=context)


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
    template = {'form': {'button': 'edit'}}
    context = {'resource_group': resource_group, 'resource': resource, 'form': form, 'breadcrumbs': breadcrumbs,
               'template': template}
    return render(request, 'generics/create_page.html', context)
