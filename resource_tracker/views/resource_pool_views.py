import logging

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django_celery_results.models import TaskResult

from resource_tracker.filters.resource_pool_filter import ResourcePoolFilter
from resource_tracker.forms import ResourcePoolForm, ResourcePoolAttributeDefinitionForm
from resource_tracker.models import ResourcePool, ResourcePoolAttributeDefinition
from resource_tracker.tables.resource_pool_attribute_definition_table import ResourcePoolAttributeDefinitionTable
from resource_tracker.views.tag_session_manager import tag_session_manager
from service_catalog.tasks import async_update_all_consumed_and_produced

logger = logging.getLogger(__name__)


@user_passes_test(lambda u: u.is_superuser)
def resource_pool_list(request):
    redirect_url = tag_session_manager(request)
    if redirect_url:
        return redirect_url

    resource_pool_filter = ResourcePoolFilter(request.GET, queryset=ResourcePool.objects.all())
    resource_pool_filter.is_valid()

    all_attributes = ResourcePoolAttributeDefinition.objects.filter(resource_pool__in=resource_pool_filter.qs)

    dict_of_attributes = dict()
    list_attribute_name = list(set([x.name for x in all_attributes]))

    for attribute_def in all_attributes:
        attribute_json = {
            "produced": attribute_def.total_produced,
            "p_factor": attribute_def.over_commitment_producers,
            "consumed": attribute_def.total_consumed,
            "c_factor": attribute_def.over_commitment_consumers,
            "available": attribute_def.available,
        }
        if attribute_def.resource_pool.name not in dict_of_attributes:
            dict_of_attributes[attribute_def.resource_pool.name] = dict()
        if attribute_def.name not in dict_of_attributes[attribute_def.resource_pool.name]:
            dict_of_attributes[attribute_def.resource_pool.name][attribute_def.name] = dict()
        dict_of_attributes[attribute_def.resource_pool.name][attribute_def.name] = attribute_json

    print(dict_of_attributes)
    print(list_attribute_name)

    returned_list = list()

    for pool_name, attributes in dict_of_attributes.items():
        default_dict = {
            "produced": "",
            "p_factor": "",
            "consumed": "",
            "c_factor": "",
            "available": "",
        }
        new_pool = {
            "pool_name": pool_name,
            "list_attribute": list()
        }
        for attribute_name_to_have in list_attribute_name:
            new_pool["list_attribute"].append(dict_of_attributes[pool_name].get(attribute_name_to_have, default_dict))
        returned_list.append(new_pool)
    print(returned_list)
    return render(request, 'resource_tracking/resource_pool/resource-pool-list.html',
                  {'resource_pools': returned_list,
                   'resource_pools_filter': resource_pool_filter,
                   'list_attribute_name': list_attribute_name,
                   'title': "Resource pools"})


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
    context = {
        'form': form,
        'resource_pool': resource_pool,
        'attribute_table': attribute_table,
        'breadcrumbs': breadcrumbs,
        'action': 'edit',
        'html_button_path': 'resource_tracking/resource_pool/resource-pool-delete-button.html'
    }
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
    task = async_update_all_consumed_and_produced.delay(resource_pool_id)
    task_result = TaskResult(task_id=task.task_id)
    task_result.save()
    request.session['task_id'] = task_result.id
    if 'HTTP_REFERER' in request.META:
        return redirect(request.META['HTTP_REFERER'])
    return redirect(reverse('resource_tracker:resource_pool_list'))


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
