from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from guardian.shortcuts import get_objects_for_user
from django.template.defaulttags import register


@register.filter(name='map_badge_instance_state')
def map_badge_instance_state(value):
    map_dict = {
        "PENDING": "bg-secondary",
        "PROVISIONING": "bg-primary",
        "PROVISION_FAILED": "bg-warning",
        "AVAILABLE": "bg-success",
        "DELETE_FAILED": "bg-warning",
        "DELETING": "bg-primary",
        "UPDATING": "bg-primary",
        "UPDATE_FAILED": "bg-warning",
        "DELETED": "bg-danger",
        "ARCHIVED": "bg-dark",
    }
    return map_dict[value]


@login_required
def customer_instance_list(request):
    instances = get_objects_for_user(request.user, 'service_catalog.view_instance')
    return render(request, 'customer/instance/instance-list.html', {'instances': instances})
