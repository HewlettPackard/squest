from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from resource_tracker.forms import ResourceGroupAttributeDefinitionForm, ResourceForm
from resource_tracker.models import ResourceGroup, ResourceGroupAttributeDefinition, Resource


@user_passes_test(lambda u: u.is_superuser)
def resource_group_resource_list(request, resource_group_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)

    list_attribute_name = list()
    for resource in resource_group.resources.all():
        for attribute in resource.attributes.all():
            if attribute.attribute_type.name not in list_attribute_name:
                list_attribute_name.append(attribute.attribute_type.name)

    return render(request, 'resource_tracking/resource_group/resources/resource-list.html',
                  {'resource_group': resource_group,
                   'list_attribute_name': list_attribute_name})


@user_passes_test(lambda u: u.is_superuser)
def resource_group_resource_delete(request, resource_group_id, resource_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    resource = get_object_or_404(Resource, id=resource_id)
    if request.method == "POST":
        resource.delete()
        return redirect("resource_tracker:resource_group_resource_list", resource_group_id)
    context = {
        "resource_group": resource_group,
        "resource": resource
    }
    return render(request, "resource_tracking/resource_group/resources/resource-delete.html", context)


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
    return render(request, 'resource_tracking/resource_group/resources/resource-create.html',
                  {'resource_group': resource_group, 'form': form})


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
    return render(request, 'resource_tracking/resource_group/resources/resource-edit.html',
                  {'resource_group': resource_group, 'resource': resource, 'form': form})
