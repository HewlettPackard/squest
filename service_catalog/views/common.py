from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render

from service_catalog.models import Request, Instance


@login_required
def home(request):
    if request.user.is_superuser:
        context = {
            "total_request": Request.objects.filter(state="SUBMITTED").count(),
            "total_instance": Instance.objects.filter(state="AVAILABLE").count(),
            "total_user": User.objects.all().count()
        }
        return render(request, 'admin/dashboard.html', context=context)
    else:
        return render(request, 'customer/dashboard.html')
