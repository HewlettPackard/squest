import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from guardian.decorators import permission_required_or_403
from guardian.shortcuts import get_objects_for_user

from service_catalog.models import Instance


@login_required
def customer_instance_list(request):
    instances = get_objects_for_user(request.user, 'service_catalog.view_instance')
    return render(request, 'customer/instance/instance-list.html', {'instances': instances})


@permission_required_or_403('service_catalog.view_instance', (Instance, 'id', 'instance_id'))
def customer_instance_details(request, instance_id):

    instance = get_object_or_404(Instance, id=instance_id)
    spec_json_pretty = json.dumps(instance.spec)
    print(spec_json_pretty)
    return render(request, 'customer/instance/instance-details.html', {'instance': instance,
                                                                       'spec_json_pretty': spec_json_pretty})
