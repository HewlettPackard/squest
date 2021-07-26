from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect

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
def ajax_load_model_state(request):
    model = request.GET.get('model')
    print(model)
    print(InstanceState.choices)
    options = [('', '----------')]
    if model == "Instance":
        options = InstanceState.choices
    if model == "Request":
        options = RequestState.choices
    return render(request, 'service_catalog/settings/global_hooks/state-dropdown-list-option.html',
                  {'options': options})
