from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def profile(request):
    breadcrumbs = [
        {'text': 'User details', 'url': ''},
    ]
    context = {'breadcrumbs': breadcrumbs}
    return render(request, 'profiles/profile.html', context=context)
