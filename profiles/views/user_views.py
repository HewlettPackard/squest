from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render
from resource_tracker.filtersets import UserFilter


@user_passes_test(lambda u: u.is_superuser)
def user_list(request):
    users = User.objects.all()
    users_filtered = UserFilter(request.GET, queryset=users)
    context = {'users': users_filtered}
    return render(request, 'profiles/user-list.html', context)
