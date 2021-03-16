from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from guardian.shortcuts import get_objects_for_user


@login_required
def customer_request_list(request):
    requests = get_objects_for_user(request.user, 'service_catalog.view_request')
    print(requests)
    return render(request, 'customer/request/request-list.html', {'requests': requests})
