from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from guardian.shortcuts import get_objects_for_user


@login_required
def customer_instance_list(request):
    instances = get_objects_for_user(request.user, 'service_catalog.view_instance')
    return render(request, 'customer/instance/instance-list.html', {'instances': instances})
