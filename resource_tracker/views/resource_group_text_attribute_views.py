from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from resource_tracker.forms import ResourceGroupTextAttributeDefinitionForm
from resource_tracker.models import ResourceGroup, ResourceGroupTextAttributeDefinition


@user_passes_test(lambda u: u.is_superuser)
def resource_group_text_attribute_create(request, resource_group_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    if request.method == 'POST':
        form = ResourceGroupTextAttributeDefinitionForm(request.POST)
        form.resource_group = resource_group  # give the resource_group so the form can validate the unique together
        if form.is_valid():
            return redirect("resource_tracker:resource_group_edit", resource_group.id)
    else:
        form = ResourceGroupTextAttributeDefinitionForm()
    breadcrumbs = [
        {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
        {'text': resource_group.name,
         'url': reverse('resource_tracker:resource_group_edit', args=[resource_group_id])},
        {'text': 'Create a new text attribute', 'url': ""},
    ]
    context = {'form': form, 'resource_group': resource_group, 'breadcrumbs': breadcrumbs, 'action': 'create'}
    return render(request, 'resource_tracking/resource_group/attributes/attribute-create.html', context)


@user_passes_test(lambda u: u.is_superuser)
def resource_group_text_attribute_edit(request, resource_group_id, attribute_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    attribute = get_object_or_404(ResourceGroupTextAttributeDefinition, id=attribute_id)
    form = ResourceGroupTextAttributeDefinitionForm(request.POST or None, instance=attribute)
    form.resource_group = resource_group
    if form.is_valid():
        return redirect("resource_tracker:resource_group_edit", resource_group.id)
    breadcrumbs = [
        {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
        {'text': resource_group.name,
         'url': reverse('resource_tracker:resource_group_edit', args=[resource_group_id])},
        {'text': attribute.name, 'url': ""},
    ]
    context = {'form': form, 'attribute': attribute, 'resource_group': resource_group, 'breadcrumbs': breadcrumbs, 'action': 'edit'}
    return render(request, 'resource_tracking/resource_group/attributes/attribute-edit.html', context)


@user_passes_test(lambda u: u.is_superuser)
def resource_group_text_attribute_delete(request, resource_group_id, attribute_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    attribute = get_object_or_404(ResourceGroupTextAttributeDefinition, id=attribute_id)
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
