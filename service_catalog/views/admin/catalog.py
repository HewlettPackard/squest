from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from service_catalog.forms import ServiceForm
from service_catalog.models import Service, Operation


@user_passes_test(lambda u: u.is_superuser)
def service(request):
    services = Service.objects.all()
    return render(request, 'catalog/service-list.html', {'services': services})


@user_passes_test(lambda u: u.is_superuser)
def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            new_instance = form.save()
            # create the first operation of type create that link this service to a job template
            job_template = form.cleaned_data['job_template']
            Operation.objects.create(name=new_instance.name,
                                     service=new_instance,
                                     job_template=job_template)
            return redirect('settings_catalog')
    else:
        form = ServiceForm()

    return render(request, 'catalog/add_service.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def service_operations(request, service_id):
    target_service = get_object_or_404(Service, id=service_id)
    operations = Operation.objects.filter(service=target_service)
    context = {
        "operations": operations,
        "service": target_service
    }
    return render(request, "catalog/service_operations.html", context)


@user_passes_test(lambda u: u.is_superuser)
def delete_service(request, service_id):
    target_service = get_object_or_404(Service, id=service_id)
    if request.method == "POST":
        target_service.delete()
        return redirect(service)
    context = {
        "object": target_service
    }
    return render(request, "catalog/confirm_delete_service.html", context)
