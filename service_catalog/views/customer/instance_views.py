import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from guardian.decorators import permission_required_or_403
from guardian.shortcuts import get_objects_for_user

from service_catalog.forms import OperationRequestForm
from service_catalog.models import Instance, Operation
from service_catalog.models.operations import OperationType


@login_required
def customer_instance_list(request):
    instances = get_objects_for_user(request.user, 'service_catalog.view_instance')
    return render(request, 'customer/instance/instance-list.html', {'instances': instances})


@permission_required_or_403('service_catalog.view_instance', (Instance, 'id', 'instance_id'))
def customer_instance_details(request, instance_id):

    instance = get_object_or_404(Instance, id=instance_id)
    spec_json_pretty = json.dumps(instance.spec)
    print(spec_json_pretty)

    operations = Operation.objects.filter(service=instance.service,
                                          type__in=[OperationType.UPDATE, OperationType.DELETE])
    context = {'instance': instance,
               'spec_json_pretty': spec_json_pretty,
               'operations': operations}

    return render(request, 'customer/instance/instance-details.html', context=context)


@permission_required_or_403('service_catalog.change_instance', (Instance, 'id', 'instance_id'))
def customer_instance_request_new_operation(request, instance_id, operation_id):
    instance = get_object_or_404(Instance, id=instance_id)
    operation = get_object_or_404(Operation, id=operation_id)

    allowed_operations = Operation.objects.filter(service=instance.service,
                                                  type__in=[OperationType.UPDATE, OperationType.DELETE])

    if operation not in allowed_operations:
        raise PermissionError

    parameters = {
        'operation_id': operation_id,
        'instance_id': instance_id
    }
    if request.method == 'POST':
        form = OperationRequestForm(request.user, request.POST, **parameters)
        if form.is_valid():
            form.save()
            return redirect('customer_request_list')
    else:
        form = OperationRequestForm(request.user, **parameters)

    return render(request, 'customer/instance/instance-request-operation.html', {'form': form,
                                                                                 'operation': operation,
                                                                                 'instance': instance})
