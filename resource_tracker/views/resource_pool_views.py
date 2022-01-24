from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from resource_tracker.filters.resource_pool_filter import ResourcePoolFilter
from resource_tracker.forms import ResourcePoolForm, ResourcePoolAttributeDefinitionForm
from resource_tracker.models import ResourcePool, ResourcePoolAttributeDefinition
from resource_tracker.tables.resource_pool_attribute_definition_table import ResourcePoolAttributeDefinitionTable


@user_passes_test(lambda u: u.is_superuser)
def resource_pool_list(request):
    resource_pool_list = ResourcePool.objects.all()
    resource_pool_filtered = ResourcePoolFilter(request.GET, queryset=resource_pool_list)
    return render(request, 'resource_tracking/resource_pool/resource-pool-list.html',
                  {'resource_pools': resource_pool_filtered, 'title': "Resource pools"})


@user_passes_test(lambda u: u.is_superuser)
def resource_pool_create(request):
    if request.method == 'POST':
        form = ResourcePoolForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("resource_tracker:resource_pool_list")
    else:
        form = ResourcePoolForm()
    breadcrumbs = [
        {'text': 'Resource pools', 'url': reverse('resource_tracker:resource_pool_list')},
        {'text': 'Create a new resource pool', 'url': ""},
    ]
    context = {'form': form, 'breadcrumbs': breadcrumbs, 'action': 'create'}
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def resource_pool_edit(request, resource_pool_id):
    resource_pool = get_object_or_404(ResourcePool, id=resource_pool_id)
    form = ResourcePoolForm(request.POST or None, instance=resource_pool)
    if form.is_valid():
        form.save()
        return redirect("resource_tracker:resource_pool_list")
    attribute_table = ResourcePoolAttributeDefinitionTable(resource_pool.attribute_definitions.all())
    breadcrumbs = [
        {'text': 'Resource pools', 'url': reverse('resource_tracker:resource_pool_list')},
        {'text': resource_pool.name, 'url': ""},
    ]
    context = {'form': form, 'resource_pool': resource_pool, 'attribute_table': attribute_table, 'breadcrumbs': breadcrumbs, 'action': 'edit'}
    return render(request, 'resource_tracking/resource_pool/resource-pool-edit.html', context)


@user_passes_test(lambda u: u.is_superuser)
def resource_pool_delete(request, resource_pool_id):
    resource_pool = get_object_or_404(ResourcePool, id=resource_pool_id)
    if request.method == 'POST':
        # need to update all resource group that use this pool to set producer/consumer to None
        for pool_attribute in resource_pool.attribute_definitions.all():
            pool_attribute.remove_all_producer()
            pool_attribute.remove_all_consumer()
        # now delete all attribute and then the pool itself
        resource_pool.attribute_definitions.all().delete()
        resource_pool.delete()
        return redirect("resource_tracker:resource_pool_list")
    breadcrumbs = [
        {'text': 'Resource pools', 'url': reverse('resource_tracker:resource_pool_list')},
        {'text': resource_pool.name, 'url': ""},
    ]
    context = {'resource_pool': resource_pool, 'breadcrumbs': breadcrumbs}
    return render(request, 'resource_tracking/resource_pool/resource-pool-delete.html', context)


@user_passes_test(lambda u: u.is_superuser)
def resource_pool_refresh_consumption(request, resource_pool_id):
    resource_pool = get_object_or_404(ResourcePool, id=resource_pool_id)
    resource_pool.update_all_consumed_and_produced()
    return redirect(request.META['HTTP_REFERER'])


@user_passes_test(lambda u: u.is_superuser)
def resource_pool_attribute_create(request, resource_pool_id):
    resource_pool = get_object_or_404(ResourcePool, id=resource_pool_id)
    if request.method == 'POST':
        form = ResourcePoolAttributeDefinitionForm(request.POST)
        form.resource_pool = resource_pool  # give the resource_pool so the form can validate the unique together
        if form.is_valid():
            new_attribute = form.save()
            new_attribute.resource_pool = resource_pool
            new_attribute.save()
            return redirect("resource_tracker:resource_pool_edit", resource_pool.id)
    else:
        form = ResourcePoolAttributeDefinitionForm()
    breadcrumbs = [
        {'text': 'Resource pools', 'url': reverse('resource_tracker:resource_pool_list')},
        {'text': resource_pool.name, 'url': reverse('resource_tracker:resource_pool_edit', args=[resource_pool_id])},
        {'text': 'Create a new attribute', 'url': ""},
    ]
    context = {'form': form, 'resource_pool': resource_pool, 'breadcrumbs': breadcrumbs, 'action': 'create'}
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def resource_pool_attribute_delete(request, resource_pool_id, attribute_id):
    resource_pool = get_object_or_404(ResourcePool, id=resource_pool_id)
    attribute = get_object_or_404(ResourcePoolAttributeDefinition, id=attribute_id)
    if request.method == "POST":
        attribute.remove_all_consumer()
        attribute.remove_all_producer()
        attribute.delete()
        return redirect("resource_tracker:resource_pool_edit", resource_pool.id)
    breadcrumbs = [
        {'text': 'Resource pools', 'url': reverse('resource_tracker:resource_pool_list')},
        {'text': resource_pool.name, 'url': reverse('resource_tracker:resource_pool_edit', args=[resource_pool_id])},
        {'text': attribute.name, 'url': ""},
    ]
    context = {
        "resource_pool": resource_pool,
        "attribute": attribute,
        'breadcrumbs': breadcrumbs
    }
    return render(request, "resource_tracking/resource_pool/attributes/attribute-delete.html", context)


@user_passes_test(lambda u: u.is_superuser)
def resource_pool_attribute_edit(request, resource_pool_id, attribute_id):
    resource_pool = get_object_or_404(ResourcePool, id=resource_pool_id)
    attribute = get_object_or_404(ResourcePoolAttributeDefinition, id=attribute_id)
    form = ResourcePoolAttributeDefinitionForm(request.POST or None, instance=attribute)
    if form.is_valid():
        form.save()
        return redirect("resource_tracker:resource_pool_edit", resource_pool.id)
    breadcrumbs = [
        {'text': 'Resource pools', 'url': reverse('resource_tracker:resource_pool_list')},
        {'text': resource_pool.name, 'url': reverse('resource_tracker:resource_pool_edit', args=[resource_pool_id])},
        {'text': 'Create a new attribute', 'url': ""},
    ]
    context = {'form': form, 'attribute': attribute, 'resource_pool': resource_pool, 'breadcrumbs': breadcrumbs,
               'action': 'edit'}
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def resource_pool_attribute_producer_list(request, resource_pool_id, attribute_id):
    resource_pool = get_object_or_404(ResourcePool, id=resource_pool_id)
    attribute = get_object_or_404(ResourcePoolAttributeDefinition, id=attribute_id)
    breadcrumbs = [
        {'text': 'Resource pools', 'url': reverse('resource_tracker:resource_pool_list')},
        {'text': resource_pool.name, 'url': ""},
        {'text': attribute.name, 'url': ""},
        {'text': 'Producers', 'url': ""}
    ]
    context = {'attribute': attribute, 'resource_pool': resource_pool, 'breadcrumbs': breadcrumbs}
    return render(request, 'resource_tracking/resource_pool/attributes/producer-list.html', context)


@user_passes_test(lambda u: u.is_superuser)
def resource_pool_attribute_consumer_list(request, resource_pool_id, attribute_id):
    resource_pool = get_object_or_404(ResourcePool, id=resource_pool_id)
    attribute = get_object_or_404(ResourcePoolAttributeDefinition, id=attribute_id)
    breadcrumbs = [
        {'text': 'Resource pools', 'url': reverse('resource_tracker:resource_pool_list')},
        {'text': resource_pool.name, 'url': ""},
        {'text': attribute.name, 'url': ""},
        {'text': 'Consumers', 'url': ""}
    ]
    context = {'attribute': attribute, 'resource_pool': resource_pool, 'breadcrumbs': breadcrumbs}
    return render(request, 'resource_tracking/resource_pool/attributes/consumer-list.html', context)
