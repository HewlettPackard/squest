from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from resource_tracker.forms import ResourceGroupForm, ResourceGroupAttributeDefinitionForm
from resource_tracker.models import ResourceGroup, ResourceGroupAttributeDefinition


@user_passes_test(lambda u: u.is_superuser)
def resource_group_list(request):
    resource_groups = ResourceGroup.objects.all()
    return render(request, 'resource_tracking/resource_group/resource-group-list.html',
                  {'resource_groups': resource_groups})


@user_passes_test(lambda u: u.is_superuser)
def resource_group_attribute_list(request, resource_group_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    return render(request, 'resource_tracking/resource_group/attributes/attribute-list.html',
                  {'resource_group': resource_group})


@user_passes_test(lambda u: u.is_superuser)
def resource_group_attribute_create(request, resource_group_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    if request.method == 'POST':
        form = ResourceGroupAttributeDefinitionForm(request.POST)
        if form.is_valid():
            new_attribute = form.save()
            new_attribute.resource_group_definition = resource_group
            new_attribute.save()
            return redirect(resource_group_attribute_list, resource_group.id)
    else:
        form = ResourceGroupAttributeDefinitionForm()

    return render(request,
                  'resource_tracking/resource_group/attributes/attribute-create.html',
                  {'form': form, 'resource_group': resource_group})


@user_passes_test(lambda u: u.is_superuser)
def resource_group_create(request):
    if request.method == 'POST':
        form = ResourceGroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(resource_group_list)
    else:
        form = ResourceGroupForm()
    return render(request, 'resource_tracking/resource_group/resource-group-create.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def resource_group_attribute_edit(request, resource_group_id, attribute_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    attribute = get_object_or_404(ResourceGroupAttributeDefinition, id=attribute_id)
    form = ResourceGroupAttributeDefinitionForm(request.POST or None, instance=attribute)
    if form.is_valid():
        form.save()
        return redirect(resource_group_attribute_list, attribute.resource_group_definition.id)
    return render(request, 'resource_tracking/resource_group/attributes/attribute-edit.html',
                  {'form': form, 'attribute': attribute, 'resource_group': resource_group})


@user_passes_test(lambda u: u.is_superuser)
def resource_group_attribute_delete(request, resource_group_id, attribute_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    attribute = get_object_or_404(ResourceGroupAttributeDefinition, id=attribute_id)
    if request.method == "POST":
        attribute.delete()
        return redirect(resource_group_attribute_list, attribute.resource_group_definition.id)
    context = {
        "resource_group": resource_group,
        "attribute": attribute
    }
    return render(request, "resource_tracking/resource_group/attributes/attribute-delete.html", context)


@user_passes_test(lambda u: u.is_superuser)
def resource_group_resource_list(request, resource_group_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)

    list_attribute_name = list()
    for resource in resource_group.resources.all():
        for attribute in resource.attributes.all():
            if attribute.name not in list_attribute_name:
                list_attribute_name.append(attribute.name)

    return render(request, 'resource_tracking/resource_group/resources/resource-list.html',
                  {'resource_group': resource_group,
                   'list_attribute_name': list_attribute_name})
