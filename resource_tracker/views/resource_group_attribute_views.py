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
            resource_group.add_attribute_definition(name=form.cleaned_data["name"],
                                                    produce_for=form.cleaned_data["produce_for"],
                                                    consume_from=form.cleaned_data["consume_from"],
                                                    help_text=form.cleaned_data["help_text"])
            return redirect("resource_tracker:resource_group_edit", resource_group.id)
    else:
        form = ResourceGroupAttributeDefinitionForm()
    breadcrumbs = [
        {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
        {'text': resource_group.name,
         'url': reverse('resource_tracker:resource_group_edit', args=[resource_group_id])},
        {'text': 'Create a new attribute', 'url': ""},
    ]
    context = {'form': form, 'resource_group': resource_group, 'breadcrumbs': breadcrumbs, 'action': 'create'}
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def resource_group_attribute_edit(request, resource_group_id, attribute_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    attribute = get_object_or_404(ResourceGroupAttributeDefinition, id=attribute_id)
    consume_from_before = attribute.consume_from
    produce_for_before = attribute.produce_for
    form = ResourceGroupAttributeDefinitionForm(request.POST or None, instance=attribute)
    form.resource_group = resource_group
    if form.is_valid():
        resource_group.edit_attribute_definition(attribute_id=attribute.id,
                                                 name=form.cleaned_data["name"],
                                                 produce_for=form.cleaned_data["produce_for"],
                                                 consume_from=form.cleaned_data["consume_from"],
                                                 help_text=form.cleaned_data["help_text"])
        # if the new pool attribute to produce or consume has changed, we need to update it
        if consume_from_before is not None and consume_from_before.id != form.cleaned_data["consume_from"]:
            consume_from_before.calculate_total_consumed()
        if produce_for_before is not None and produce_for_before.id != form.cleaned_data["produce_for"]:
            produce_for_before.calculate_total_produced()
        return redirect("resource_tracker:resource_group_edit", resource_group.id)
    breadcrumbs = [
        {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
        {'text': resource_group.name,
         'url': reverse('resource_tracker:resource_group_edit', args=[resource_group_id])},
        {'text': attribute.name, 'url': ""},
    ]
    context = {'form': form, 'attribute': attribute, 'resource_group': resource_group, 'breadcrumbs': breadcrumbs,
               'action': 'edit'}
    return render(request, 'generics/generic_form.html', context)


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
        'breadcrumbs': breadcrumbs,
        "attribute_type": "attribute"
    }
    return render(request, "resource_tracking/resource_group/attributes/attribute-delete.html", context)
