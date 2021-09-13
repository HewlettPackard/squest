from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from service_catalog.forms import GlobalHookForm
from service_catalog.models import GlobalHook
from service_catalog.models.instance import InstanceState
from service_catalog.models.request import RequestState


@user_passes_test(lambda u: u.is_superuser)
def global_hook_create(request):
    if request.method == 'POST':
        form = GlobalHookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('service_catalog:global_hook_list')
    else:
        form = GlobalHookForm()
    breadcrumbs = [
        {'text': 'Global hooks', 'url': reverse('service_catalog:global_hook_list')},
        {'text': "Create a new global hook", 'url': ""}
    ]
    context = {'form': form, 'breadcrumbs': breadcrumbs}
    return render(request, 'service_catalog/settings/global_hooks/global-hook-create.html', context)


@user_passes_test(lambda u: u.is_superuser)
def global_hook_edit(request, global_hook_id):
    target_global_hook = get_object_or_404(GlobalHook, id=global_hook_id)
    form = GlobalHookForm(request.POST or None, instance=target_global_hook)
    if form.is_valid():
        form.save()
        return redirect('service_catalog:global_hook_list')
    breadcrumbs = [
        {'text': 'Global hooks', 'url': reverse('service_catalog:global_hook_list')},
        {'text': target_global_hook.name, 'url': ""}
    ]
    context = {'form': form,
               'global_hook': target_global_hook,
               'breadcrumbs': breadcrumbs
               }
    return render(request, 'service_catalog/settings/global_hooks/global-hook-edit.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def global_hook_delete(request, global_hook_id):
    target_global_hook = get_object_or_404(GlobalHook, id=global_hook_id)
    if request.method == "POST":
        target_global_hook.delete()
        return redirect('service_catalog:global_hook_list')
    breadcrumbs = [
        {'text': 'Global hooks', 'url': reverse('service_catalog:global_hook_list')},
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
