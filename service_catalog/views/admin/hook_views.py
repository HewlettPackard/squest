from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from service_catalog.forms import GlobalHookForm
from service_catalog.models.services import Service
from service_catalog.models.state_hooks import GlobalHook
from service_catalog.models.instance import InstanceState
from service_catalog.models.request import RequestState


@user_passes_test(lambda u: u.is_superuser)
def global_hook_create(request):
    if request.method == 'POST':
        form = GlobalHookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('service_catalog:globalhook_list')
    else:
        form = GlobalHookForm()
    breadcrumbs = [
        {'text': 'Global hooks', 'url': reverse('service_catalog:globalhook_list')},
        {'text': "Create a new global hook", 'url': ""}
    ]
    context = {'form': form, 'breadcrumbs': breadcrumbs}
    return render(request, 'service_catalog/settings/global_hooks/global-hook-create.html', context)


@user_passes_test(lambda u: u.is_superuser)
def global_hook_edit(request, globalhook_id):
    target_global_hook = get_object_or_404(GlobalHook, id=globalhook_id)
    form = GlobalHookForm(request.POST or None, instance=target_global_hook)
    if form.is_valid():
        form.save()
        return redirect('service_catalog:globalhook_list')
    breadcrumbs = [
        {'text': 'Global hooks', 'url': reverse('service_catalog:globalhook_list')},
        {'text': target_global_hook.name, 'url': ""}
    ]
    context = {'form': form,
               'global_hook': target_global_hook,
               'breadcrumbs': breadcrumbs
               }
    return render(request, 'service_catalog/settings/global_hooks/global-hook-edit.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def global_hook_delete(request, globalhook_id):
    target_global_hook = get_object_or_404(GlobalHook, id=globalhook_id)
    if request.method == "POST":
        target_global_hook.delete()
        return redirect('service_catalog:globalhook_list')
    breadcrumbs = [
        {'text': 'Global hooks', 'url': reverse('service_catalog:globalhook_list')},
        {'text': target_global_hook.name, 'url': ""}
    ]
    context = {
        'global_hook': target_global_hook,
        'breadcrumbs': breadcrumbs
    }
    return render(request, "service_catalog/settings/global_hooks/global-hook-delete.html", context)


@user_passes_test(lambda u: u.is_superuser)
def ajax_load_model_state(request):
    model = request.GET.get('model')
    options = [('', '----------')]
    if model == "Instance":
        options = InstanceState.choices
    if model == "Request":
        options = RequestState.choices
    return render(request, 'service_catalog/settings/global_hooks/state-dropdown-list-option.html',
                  {'options': options})


@user_passes_test(lambda u: u.is_superuser)
def ajax_load_service_operations(request):
    service_id = int(request.GET.get('service'))
    options = [('', '----------')]
    if service_id != 0:
        services = Service.objects.filter(id=service_id)
        if services.count() == 1:
            options = [(operation.id, operation.name) for operation in services[0].operations.all()]
    return render(request, 'service_catalog/settings/global_hooks/state-dropdown-list-option.html',
                  {'options': options})
