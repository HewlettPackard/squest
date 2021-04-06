import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django_fsm import can_proceed
from guardian.decorators import permission_required_or_403
from guardian.shortcuts import get_objects_for_user

from service_catalog.forms import OperationRequestForm, SupportRequestForm, Support
from service_catalog.models import Instance, Operation
from service_catalog.models.instance import InstanceState
from service_catalog.models.operations import OperationType


@login_required
def customer_instance_list(request):
    instances = get_objects_for_user(request.user, 'service_catalog.view_instance')
    return render(request, 'customer/instance/instance-list.html', {'instances': instances})


@permission_required_or_403('service_catalog.view_instance', (Instance, 'id', 'instance_id'))
def customer_instance_details(request, instance_id):

    instance = get_object_or_404(Instance, id=instance_id)
    spec_json_pretty = json.dumps(instance.spec)

    operations = Operation.objects.filter(service=instance.service,
                                          type__in=[OperationType.UPDATE, OperationType.DELETE])

    supports = Support.objects.filter(instance=instance)
    context = {'instance': instance,
               'spec_json_pretty': spec_json_pretty,
               'operations': operations,
               'supports': supports}

    return render(request, 'customer/instance/instance-details.html', context=context)


@permission_required_or_403('service_catalog.change_instance', (Instance, 'id', 'instance_id'))
def customer_instance_request_new_operation(request, instance_id, operation_id):
    instance = get_object_or_404(Instance, id=instance_id)
    if instance.state not in [InstanceState.AVAILABLE, InstanceState.UPDATING]:
        raise PermissionDenied
    operation = get_object_or_404(Operation, id=operation_id)
    allowed_operations = Operation.objects.filter(service=instance.service,
                                                  type__in=[OperationType.UPDATE, OperationType.DELETE])

    if operation not in allowed_operations:
        raise PermissionDenied

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


@permission_required_or_403('service_catalog.change_instance', (Instance, 'id', 'instance_id'))
def customer_instance_archive(request, instance_id):
    target_instance = get_object_or_404(Instance, id=instance_id)
    if request.method == "POST":
        if not can_proceed(target_instance.archive):
            raise PermissionDenied
        target_instance.archive()
        target_instance.save()

        return redirect(customer_instance_list)
    context = {
        "instance": target_instance
    }
    return render(request, "customer/instance/instance-archive.html", context)


@permission_required_or_403('service_catalog.change_instance', (Instance, 'id', 'instance_id'))
def customer_instance_new_support(request, instance_id):
    target_instance = get_object_or_404(Instance, id=instance_id)
    parameters = {
        'instance_id': instance_id
    }
    if request.method == 'POST':
        form = SupportRequestForm(request.user, request.POST, **parameters)
        if form.is_valid():
            form.save()
            return redirect('customer_instance_details', target_instance.id)
    else:
        form = SupportRequestForm(request.user, **parameters)

    return render(request, 'customer/instance/support/support-create.html', {'form': form,
                                                                             'instance': target_instance})
