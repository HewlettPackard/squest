from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from profiles.models import Token


@login_required
def profile(request):
    tokens = Token.objects.filter(user=request.user)
    context = {
        'tokens': tokens,
        'title': "User details"
    }
    return render(request, 'profiles/profile.html', context)
