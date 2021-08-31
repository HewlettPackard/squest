from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from profiles.forms.token_forms import TokenForm
from profiles.models import Token


@login_required
def profile(request):
    token, created = Token.objects.get_or_create(user=request.user)
    context = {
        'token_api': token,
        'current_tab': 'details',
        'token_api_is_expired': token.is_expired()
    }
    if 'current_tab' in request.session:
        context['current_tab'] = request.session['current_tab']
        del request.session['current_tab']
    return render(request, 'profiles/profile.html', context)


def token_generate(request, token_id):
    token = get_object_or_404(Token, id=token_id)
    token.update_key()
    request.session['current_tab'] = 'tokens'
    return redirect('profiles:profile')


def token_edit(request, token_id):
    token = get_object_or_404(Token, id=token_id)
    form = TokenForm(request.POST or None, instance=token)
    if form.is_valid():
        form.save()
        request.session['current_tab'] = 'tokens'
        return redirect("profiles:profile")
    breadcrumbs = [
        {'text': 'Profile', 'url': reverse('profiles:profile')},
        {'text': 'Token', 'url': ''},
    ]
    context = {'form': form, 'breadcrumbs': breadcrumbs, 'token_api': token, 'action': 'edit'}
    return render(request, 'profiles/token-edit.html', context)
