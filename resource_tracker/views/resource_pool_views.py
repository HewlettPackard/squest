from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from resource_tracker.forms import ResourcePoolForm, ResourcePoolAttributeDefinitionForm
from resource_tracker.models import ResourcePool, ResourcePoolAttributeDefinition


@user_passes_test(lambda u: u.is_superuser)
def resource_pool_list(request):
    resource_pools = ResourcePool.objects.all()
    list_attribute_name = list()
    for resource_pool in resource_pools.all():
        for attribute in resource_pool.attributes_definition.all():
            if attribute.name not in list_attribute_name:
                list_attribute_name.append(attribute.name)
    return render(request, 'resource_tracking/resource_pool/resource-pool-list.html',
                  {'resource_pools': resource_pools,
                   'list_attribute_name': list_attribute_name})


@user_passes_test(lambda u: u.is_superuser)
def resource_pool_create(request):
    if request.method == 'POST':
        form = ResourcePoolForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(resource_pool_list)
    else:
        form = ResourcePoolForm()
    return render(request, 'resource_tracking/resource_pool/resource-pool-create.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def resource_pool_edit(request, resource_pool_id):
    resource_pool = get_object_or_404(ResourcePool, id=resource_pool_id)
    form = ResourcePoolForm(request.POST or None, instance=resource_pool)
    if form.is_valid():
        form.save()
        return redirect(resource_pool_list)
    return render(request,
                  'resource_tracking/resource_pool/resource-pool-edit.html', {'form': form,
                                                                              'resource_pool': resource_pool})


@user_passes_test(lambda u: u.is_superuser)
def resource_pool_delete(request, resource_pool_id):
    resource_pool = get_object_or_404(ResourcePool, id=resource_pool_id)
    if request.method == 'POST':
        # need to update all resource group that use this pool to set producer/consumer to None
        for pool_attribute in resource_pool.attributes_definition.all():
            pool_attribute.remove_all_producer()
            pool_attribute.remove_all_consumer()
        # now delete all attribute and then the pool itself
        resource_pool.attributes_definition.all().delete()
        resource_pool.delete()
        return redirect(resource_pool_list)

    return render(request,
                  'resource_tracking/resource_pool/resource-pool-delete.html', {'resource_pool': resource_pool})


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
            return redirect(resource_pool_edit, resource_pool.id)
    else:
        form = ResourcePoolAttributeDefinitionForm()

    return render(request,
                  'resource_tracking/resource_pool/attributes/attribute-create.html',
                  {'form': form, 'resource_pool': resource_pool})


@user_passes_test(lambda u: u.is_superuser)
def resource_pool_attribute_delete(request, resource_pool_id, attribute_id):
    resource_pool = get_object_or_404(ResourcePool, id=resource_pool_id)
    attribute = get_object_or_404(ResourcePoolAttributeDefinition, id=attribute_id)
    if request.method == "POST":
        attribute.delete()
        return redirect(resource_pool_edit, resource_pool.id)
    context = {
        "resource_pool": resource_pool,
        "attribute": attribute
    }
    return render(request, "resource_tracking/resource_pool/attributes/attribute-delete.html", context)


@user_passes_test(lambda u: u.is_superuser)
def resource_pool_attribute_edit(request, resource_pool_id, attribute_id):
    resource_pool = get_object_or_404(ResourcePool, id=resource_pool_id)
    attribute = get_object_or_404(ResourcePoolAttributeDefinition, id=attribute_id)
    form = ResourcePoolAttributeDefinitionForm(request.POST or None, instance=attribute)
    if form.is_valid():
        form.save()
        return redirect(resource_pool_edit, resource_pool.id)
    return render(request, 'resource_tracking/resource_pool/attributes/attribute-edit.html',
                  {'form': form, 'attribute': attribute, 'resource_pool': resource_pool})


@user_passes_test(lambda u: u.is_superuser)
def resource_pool_attribute_producer_list(request, resource_pool_id, attribute_id):
    resource_pool = get_object_or_404(ResourcePool, id=resource_pool_id)
    attribute = get_object_or_404(ResourcePoolAttributeDefinition, id=attribute_id)

    return render(request, 'resource_tracking/resource_pool/attributes/producer-list.html',
                  {'attribute': attribute, 'resource_pool': resource_pool})


@user_passes_test(lambda u: u.is_superuser)
def resource_pool_attribute_consumer_list(request, resource_pool_id, attribute_id):
    resource_pool = get_object_or_404(ResourcePool, id=resource_pool_id)
    attribute = get_object_or_404(ResourcePoolAttributeDefinition, id=attribute_id)

    return render(request, 'resource_tracking/resource_pool/attributes/consumer-list.html',
                  {'attribute': attribute, 'resource_pool': resource_pool})
