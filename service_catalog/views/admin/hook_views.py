from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from service_catalog.forms import GlobalHookForm
from service_catalog.models import GlobalHook
from service_catalog.models.instance import InstanceState
from service_catalog.models.request import RequestState


@user_passes_test(lambda u: u.is_superuser)
def global_hook_list(request):
    return render(request, 'service_catalog/settings/global_hooks/global-hook-list.html',
                  {'global_hooks': GlobalHook.objects.all()})


@user_passes_test(lambda u: u.is_superuser)
def global_hook_create(request):
    if request.method == 'POST':
        form = GlobalHookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('service_catalog:global_hook_list')
    else:
        form = GlobalHookForm()
    return render(request, 'service_catalog/settings/global_hooks/global-hook-create.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def global_hook_edit(request, global_hook_id):
    target_global_hook = get_object_or_404(GlobalHook, id=global_hook_id)
    form = GlobalHookForm(request.POST or None, instance=target_global_hook)
    form.fields['state'].initial = [("tt", "tt")]
    if form.is_valid():
        form.save()
        return redirect('service_catalog:global_hook_list')
    context = {'form': form,
               'global_hook': target_global_hook
               }
    return render(request, 'service_catalog/settings/global_hooks/global-hook-edit.html', context=context)


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
