from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect

from resource_tracker.forms import ResourcePoolForm
from resource_tracker.models import ResourcePool


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
