from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe

from profiles.forms.token_forms import TokenForm
from profiles.models import Token


@login_required
def token_generate(request, token_id):
    request.session['current_tab'] = 'tokens'
    token = get_object_or_404(Token, id=token_id)
    token.update_key()
    return redirect('profiles:profile')


@login_required
def token_create(request):
    request.session['current_tab'] = 'tokens'
    if request.method == 'POST':
        form = TokenForm(request.POST)
        if form.is_valid():
            token = form.save()
            token.user = request.user
            token.save()
            return redirect("profiles:profile")
    else:
        form = TokenForm()
    breadcrumbs = [
        {'text': 'Tokens', 'url': reverse('profiles:profile')},
        {'text': 'Create a new token', 'url': ""},
    ]
    context = {'form': form, 'breadcrumbs': breadcrumbs, 'token_api': form, 'action': 'create'}
    return render(request, 'profiles/token-edit.html', context)


@login_required
def token_edit(request, token_id):
    request.session['current_tab'] = 'tokens'
    token = get_object_or_404(Token, id=token_id)
    form = TokenForm(request.POST or None, instance=token)
    if form.is_valid():
        form.save()
        return redirect("profiles:profile")
    breadcrumbs = [
        {'text': 'Tokens', 'url': reverse('profiles:profile')},
        {'text': token, 'url': ''},
    ]
    context = {'form': form, 'breadcrumbs': breadcrumbs, 'token_api': token, 'action': 'edit'}
    return render(request, 'profiles/token-edit.html', context)


@login_required
def token_delete(request, token_id):
    request.session['current_tab'] = 'tokens'
    token = get_object_or_404(Token, id=token_id)
    if request.method == 'POST':
        token.delete()
        return redirect("profiles:profile")
    args = {
        "token_id": token_id,
    }
    breadcrumbs = [
        {'text': 'Tokens', 'url': reverse('profiles:profile')},
        {'text': token, 'url': ""}
    ]
    context = {
        'breadcrumbs': breadcrumbs,
        'confirm_text': mark_safe(f"Confirm deletion of <strong>{token}</strong>?"),
        'action_url': reverse('profiles:token_delete', kwargs=args),
        'button_text': 'Delete',
        'details': None
    }
    return render(request, 'generics/confirm-delete-template.html', context=context)
