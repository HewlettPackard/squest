from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

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
