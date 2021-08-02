from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from resource_tracker.forms import ResourceGroupAttributeDefinitionForm
from resource_tracker.models import ResourceGroup, ResourceGroupAttributeDefinition


@user_passes_test(lambda u: u.is_superuser)
def resource_group_attribute_create(request, resource_group_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    if request.method == 'POST':
        form = ResourceGroupAttributeDefinitionForm(request.POST)
        form.resource_group = resource_group  # give the resource_group so the form can validate the unique together
        if form.is_valid():
            new_attribute = form.save()
            new_attribute.resource_group_definition = resource_group
            new_attribute.save()
            return redirect("resource_tracker:resource_group_edit", resource_group.id)
    else:
        form = ResourceGroupAttributeDefinitionForm()
    breadcrumbs = [
        {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
        {'text': resource_group.name,
         'url': reverse('resource_tracker:resource_group_edit', args=[resource_group_id])},
        {'text': 'Create a new attribute', 'url': ""},
    ]
    context = {'form': form, 'resource_group': resource_group, 'breadcrumbs': breadcrumbs}
    return render(request, 'resource_tracking/resource_group/attributes/attribute-create.html', context)


@user_passes_test(lambda u: u.is_superuser)
def resource_group_attribute_edit(request, resource_group_id, attribute_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    attribute = get_object_or_404(ResourceGroupAttributeDefinition, id=attribute_id)
    form = ResourceGroupAttributeDefinitionForm(request.POST or None, instance=attribute)
    if form.is_valid():
        form.save()
        return redirect("resource_tracker:resource_group_edit", resource_group.id)
    breadcrumbs = [
        {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
        {'text': resource_group.name,
         'url': reverse('resource_tracker:resource_group_edit', args=[resource_group_id])},
        {'text': attribute.name, 'url': ""},
    ]
    context = {'form': form, 'attribute': attribute, 'resource_group': resource_group, 'breadcrumbs': breadcrumbs}
    return render(request, 'resource_tracking/resource_group/attributes/attribute-edit.html', context)


@user_passes_test(lambda u: u.is_superuser)
def resource_group_attribute_delete(request, resource_group_id, attribute_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    attribute = get_object_or_404(ResourceGroupAttributeDefinition, id=attribute_id)
    if request.method == "POST":
        attribute.delete()
        return redirect("resource_tracker:resource_group_edit", resource_group.id)
    breadcrumbs = [
        {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
        {'text': resource_group.name,
         'url': reverse('resource_tracker:resource_group_edit', args=[resource_group_id])},
        {'text': attribute.name, 'url': ""},
    ]
    context = {
        "resource_group": resource_group,
        "attribute": attribute,
        'breadcrumbs': breadcrumbs
    }
    return render(request, "resource_tracking/resource_group/attributes/attribute-delete.html", context)
