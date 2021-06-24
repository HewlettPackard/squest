from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from resource_tracker.forms import ResourceGroupForm
from resource_tracker.models import ResourceGroup


@user_passes_test(lambda u: u.is_superuser)
def resource_group_list(request):
    resource_groups = ResourceGroup.objects.all()
    return render(request, 'resource_tracking/resource_group/resource-group-list.html',
                  {'resource_groups': resource_groups})


@user_passes_test(lambda u: u.is_superuser)
def resource_group_edit(request, resource_group_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    form = ResourceGroupForm(request.POST or None, instance=resource_group)
    if form.is_valid():
        form.save()
        return redirect(resource_group_list)
    return render(request,
                  'resource_tracking/resource_group/resource-group-edit.html', {'form': form,
                                                                                'resource_group': resource_group})


@user_passes_test(lambda u: u.is_superuser)
def resource_group_create(request):
    if request.method == 'POST':
        form = ResourceGroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(resource_group_list)
    else:
        form = ResourceGroupForm()
    return render(request, 'resource_tracking/resource_group/resource-group-create.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def resource_group_delete(request, resource_group_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    if request.method == 'POST':
        # delete all resource attributes
        resource_group.resources.all().delete()
        resource_group.attribute_definitions.all().delete()
        resource_group.delete()
        # delete all resources
        return redirect(resource_group_list)

    return render(request,
                  'resource_tracking/resource_group/resource-group-delete.html', {'resource_group': resource_group})