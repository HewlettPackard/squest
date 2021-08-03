import json

from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django_fsm import can_proceed
from guardian.decorators import permission_required_or_403

from service_catalog.forms import OperationRequestForm, Support
from service_catalog.models import Instance, Operation
from service_catalog.models.instance import InstanceState
from service_catalog.models.operations import OperationType
from service_catalog.views import instance_new_support, instance_support_details


@permission_required_or_403('service_catalog.view_instance', (Instance, 'id', 'instance_id'))
def customer_instance_details(request, instance_id):
    instance = get_object_or_404(Instance, id=instance_id)
    if instance.state != InstanceState.AVAILABLE:
        return redirect('service_catalog:instance_list')
    spec_json_pretty = json.dumps(instance.spec)

    operations = Operation.objects.filter(service=instance.service,
                                          type__in=[OperationType.UPDATE, OperationType.DELETE])

    supports = Support.objects.filter(instance=instance)
    breadcrumbs = [
        {'text': 'Instances', 'url': reverse('service_catalog:instance_list')},
        {'text': f"{instance.name} ({instance.id})", 'url': ""},
    ]
    context = {'instance': instance,
               'spec_json_pretty': spec_json_pretty,
               'operations': operations,
               'supports': supports,
               'breadcrumbs': breadcrumbs}

    return render(request, 'service_catalog/customer/instance/instance-details.html', context=context)


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
            return redirect('service_catalog:request_list')
    else:
        form = OperationRequestForm(request.user, **parameters)
    context = {'form': form, 'operation': operation, 'instance': instance}
    return render(request, 'service_catalog/customer/instance/instance-request-operation.html', context)


@permission_required_or_403('service_catalog.change_instance', (Instance, 'id', 'instance_id'))
def customer_instance_archive(request, instance_id):
    target_instance = get_object_or_404(Instance, id=instance_id)
    if request.method == "POST":
        if not can_proceed(target_instance.archive):
            raise PermissionDenied
        target_instance.archive()
        target_instance.save()

        return redirect('service_catalog:instance_list')
    context = {
        "instance": target_instance
    }
    return render(request, "service_catalog/customer/instance/instance-archive.html", context)


@permission_required_or_403('service_catalog.change_instance', (Instance, 'id', 'instance_id'))
def customer_instance_new_support(request, instance_id):
    instance = get_object_or_404(Instance, id=instance_id)
    breadcrumbs = [
        {'text': 'Instances', 'url': reverse('service_catalog:instance_list')},
        {'text': f"{instance.name} ({instance.id})",
         'url': reverse('service_catalog:customer_instance_details', args=[instance_id])},
    ]
    return instance_new_support(request, instance_id, breadcrumbs)


@permission_required_or_403('service_catalog.change_instance', (Instance, 'id', 'instance_id'))
def customer_instance_support_details(request, instance_id, support_id):
    instance = get_object_or_404(Instance, id=instance_id)
    support = get_object_or_404(Support, id=support_id)
    breadcrumbs = [
        {'text': 'Instances', 'url': reverse('service_catalog:instance_list')},
        {'text': f"{instance.name} ({instance.id})",
         'url': reverse('service_catalog:customer_instance_details',args=[instance_id])},
        {'text': 'Support', 'url': ""},
        {'text': support.title, 'url': ""},
    ]
    return instance_support_details(request, instance_id, support_id, breadcrumbs)
