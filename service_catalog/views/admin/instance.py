import json

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from service_catalog.forms import InstanceForm
from service_catalog.models import Instance, Support
from service_catalog.models.operations import OperationType, Operation
from service_catalog.views import instance_new_support, instance_support_details


@user_passes_test(lambda u: u.is_superuser)
def admin_instance_details(request, instance_id):
    instance = get_object_or_404(Instance, id=instance_id)
    spec_json_pretty = json.dumps(instance.spec)

    supports = Support.objects.filter(instance=instance)
    operations = Operation.objects.filter(service=instance.service,
                                          type__in=[OperationType.UPDATE, OperationType.DELETE])
    breadcrumbs = [
        {'text': 'Instances', 'url': reverse('service_catalog:instance_list')},
        {'text': f"{instance.name} ({instance.id})", 'url': ""},
    ]
    context = {'instance': instance,
               'spec_json_pretty': spec_json_pretty,
               'supports': supports,
               'operations': operations,
               'breadcrumbs': breadcrumbs}

    return render(request, 'service_catalog/admin/instance/instance-details.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def admin_instance_new_support(request, instance_id):
    instance = get_object_or_404(Instance, id=instance_id)
    breadcrumbs = [
        {'text': 'Instances', 'url': reverse('service_catalog:instance_list')},
        {'text': f"{instance.name} ({instance.id})",
         'url': reverse('service_catalog:admin_instance_details', args=[instance.id])},
    ]
    return instance_new_support(request, instance_id, breadcrumbs)


@user_passes_test(lambda u: u.is_superuser)
def admin_instance_support_details(request, instance_id, support_id):
    instance = get_object_or_404(Instance, id=instance_id)
    support = get_object_or_404(Support, id=support_id)
    breadcrumbs = [
        {'text': 'Instances', 'url': reverse('service_catalog:instance_list')},
        {'text': f"{instance.name} ({instance.id})",
         'url': reverse('service_catalog:admin_instance_details', args=[instance.id])},
        {'text': 'Support', 'url': reverse('service_catalog:admin_support_list')},
        {'text': support.title, 'url': ""},
    ]
    return instance_support_details(request, instance_id, support_id, breadcrumbs)


@user_passes_test(lambda u: u.is_superuser)
def admin_instance_edit(request, instance_id):
    instance = get_object_or_404(Instance, id=instance_id)

    form = InstanceForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('service_catalog:admin_instance_details', instance.id)
    breadcrumbs = [
        {'text': 'Instances', 'url': reverse('service_catalog:instance_list')},
        {'text': f"{instance.name} ({instance.id})",
         'url': reverse('service_catalog:admin_instance_details', args=[instance_id])},
    ]
    context = {'form': form, 'instance': instance, 'breadcrumbs': breadcrumbs}
    return render(request, 'service_catalog/admin/instance/instance-edit.html', context)
