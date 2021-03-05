from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render


@login_required
def home(request):
    return render(request, 'home.html')

@user_passes_test(lambda u: u.is_superuser)
def tower(request):
    return render(request, 'tower/tower-list.html')