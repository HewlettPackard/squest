from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from profiles.models import Token


@login_required
def profile(request):
    tokens = Token.objects.filter(user=request.user)
    context = {
        'tokens': tokens,
        'current_tab': 'details'
    }
    if 'current_tab' in request.session:
        context['current_tab'] = request.session['current_tab']
        del request.session['current_tab']
    return render(request, 'profiles/profile.html', context)
