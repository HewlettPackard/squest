from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.safestring import mark_safe

from profiles.forms.scope_form import ScopeCreateRBACForm, ScopeAddRolesForm
from profiles.models import Organization, RBAC, Team, Role, Scope

from django.urls import reverse

from django.contrib.auth.models import User


@user_passes_test(lambda u: u.is_superuser)
def organization_rbac_create(request, pk):
    organization = get_object_or_404(Organization, id=pk)
    return scope_rbac_create(request, organization)


@user_passes_test(lambda u: u.is_superuser)
def team_rbac_create(request, pk):
    team = get_object_or_404(Team, id=pk)
    return scope_rbac_create(request, team, team.org.users)


def scope_rbac_create(request, scope, user_qs=None):
    form = ScopeCreateRBACForm(request.POST or None, scope=scope)
    if form.is_valid():
        form.save()
        return redirect(scope.get_absolute_url())
    breadcrumbs = [
        {'text': scope.__class__.__name__, 'url': reverse(f'profiles:{scope.__class__.__name__.lower()}_list')},
        {'text': scope,
         'url': reverse(f'profiles:{scope.__class__.__name__.lower()}_details', kwargs={"pk": scope.id})},
        {'text': f'Add RBAC', 'url': ""},
    ]
    context = {'form': form, 'object_name': "billing_group", 'breadcrumbs': breadcrumbs,
               'action': "edit"}
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def organization_rbac_delete(request, scope_id, rbac_id, user_id):
    organization = get_object_or_404(Organization, id=scope_id)
    team_name_list = RBAC.objects.filter(
        scope__in=organization.teams.all(),
        user__id=user_id
    ).values_list("scope__name", flat=True)
    details = {
        'warning_sentence': 'Warning: User still in following Teams, it will be removed from them:',
        'details_list': [f"{team}," for team in team_name_list]
    } if team_name_list else None
    return scope_rbac_delete(request, organization, rbac_id, user_id, details)


@user_passes_test(lambda u: u.is_superuser)
def team_rbac_delete(request, scope_id, rbac_id, user_id):
    team = get_object_or_404(Team, id=scope_id)
    return scope_rbac_delete(request, team, rbac_id, user_id)


def scope_rbac_delete(request, scope, rbac_id, user_id, details=None):
    rbac = get_object_or_404(RBAC, group_ptr=rbac_id)
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        scope.remove_user_in_role(user, rbac.role.name)
        return redirect(scope.get_absolute_url())
    context = {
        'breadcrumbs': [
            {'text': scope.__class__.__name__, 'url': reverse(f'profiles:{scope.__class__.__name__.lower()}_list')},
            {'text': scope,
             'url': reverse(f'profiles:{scope.__class__.__name__.lower()}_details', kwargs={"pk": scope.id})},
            {'text': "Role", 'url': ""},
            {'text': rbac.role, 'url': ""},
            {'text': user, 'url': ""},
        ],
        'action_url': reverse(f'profiles:{scope.__class__.__name__.lower()}_rbac_delete',
                              kwargs={"scope_id": scope.id, "rbac_id": rbac_id, "user_id": user_id}) + "#users",
        'confirm_text': mark_safe(f"Confirm to remove <strong>{user}</strong> from <strong>{rbac.role}</strong>?"),
        'button_text': 'Delete',
        'details': details
    }
    return render(request, 'generics/confirm-delete-template.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def organization_role_create(request, pk):
    organization = get_object_or_404(Organization, id=pk)
    return scope_role_create(request, organization)


@user_passes_test(lambda u: u.is_superuser)
def team_role_create(request, pk):
    team = get_object_or_404(Team, id=pk)
    return scope_role_create(request, team)


def scope_role_create(request, scope):
    form = ScopeAddRolesForm(request.POST or None, scope=scope)
    if form.is_valid():
        form.save()
        return redirect(scope.get_absolute_url())
    breadcrumbs = [
        {'text': scope.__class__.__name__, 'url': reverse(f'profiles:{scope.__class__.__name__.lower()}_list')},
        {'text': scope,
         'url': reverse(f'profiles:{scope.__class__.__name__.lower()}_details', kwargs={"pk": scope.pk})},
        {'text': f'Add Role', 'url': ""},
    ]
    context = {'form': form, 'breadcrumbs': breadcrumbs,
               'action': "edit"}
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def scope_role_delete(request, scope_id, pk):
    scope = get_object_or_404(Scope, id=scope_id)
    role = get_object_or_404(Role, id=pk)
    if request.method == 'POST':
        scope.roles.remove(role)
        return redirect(scope.get_absolute_url())
    breadcrumbs = [
        {'text': scope.__class__.__name__, 'url': reverse(f'profiles:{scope.__class__.__name__.lower()}_list')},
        {'text': scope,
         'url': reverse(f'profiles:{scope.__class__.__name__.lower()}_details', kwargs={"pk": scope.id})},
        {'text': "Roles", 'url': ""},
        {'text': role, 'url': ""},
    ]
    context = {
        'breadcrumbs': breadcrumbs,
        'confirm_text': mark_safe(f"Confirm to remove <strong>{role}</strong> from <strong>{scope}</strong>?"),
        'action_url': reverse(f'profiles:{scope.__class__.__name__.lower()}_role_delete',
                              kwargs={"scope_id": scope.id, "pk": pk}) + "#roles",
        'button_text': 'Delete',
        'details': None
    }
    return render(request, 'generics/confirm-delete-template.html', context=context)
