from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe
from guardian.decorators import permission_required_or_403

from profiles.forms import TeamForm, AddUserForm, UserRoleForObjectForm
from profiles.models import Role
from profiles.models.team import Team


@login_required
@permission_required_or_403('profiles.change_team', (Team, 'id', 'team_id'))
def team_edit(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    form = TeamForm(request.POST or None, instance=team)
    if form.is_valid():
        form.save()
        return redirect("profiles:team_list")
    breadcrumbs = [
        {'text': 'Teams', 'url': reverse('profiles:team_list')},
        {'text': team.name, 'url': ""},
    ]
    context = {'form': form, 'group': team, 'object_name': "team", 'breadcrumbs': breadcrumbs}
    return render(request, 'profiles/group/group-edit.html', context)


@login_required
def team_create(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save()
            team.add_user_in_role(request.user, "Admin")
            return redirect("profiles:team_list")
    else:
        form = TeamForm()
    breadcrumbs = [
        {'text': 'Teams', 'url': reverse('profiles:team_list')},
        {'text': 'Create a new team', 'url': ""},
    ]
    context = {'form': form, 'object_name': "team", 'breadcrumbs': breadcrumbs}
    return render(request, 'profiles/group/group-create.html', context)


@login_required
@permission_required_or_403('profiles.delete_team', (Team, 'id', 'team_id'))
def team_delete(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if request.method == 'POST':
        team.delete()
        return redirect("profiles:team_list")
    args = {
        "team_id": team_id,
    }
    breadcrumbs = [
        {'text': 'Teams', 'url': reverse('profiles:team_list')},
        {'text': team.name, 'url': ""}
    ]
    context = {
        'breadcrumbs': breadcrumbs,
        'confirm_text': mark_safe(f"Confirm deletion of <strong>{team.name}</strong>?"),
        'action_url': reverse('profiles:team_delete', kwargs=args),
        'button_text': 'Delete',
        'details': {'warning_sentence': 'Warning: some users are still present in this team:',
                    'details_list': [user.username for user in team.get_all_users()]
                    } if team.get_all_users() else None,
        'object_name': "team"
    }
    return render(request, 'generics/confirm-delete-template.html', context=context)


@login_required
@permission_required_or_403('profiles.change_team', (Team, 'id', 'team_id'))
def user_in_team_update(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    form = UserRoleForObjectForm(request.POST or None, object=team)
    error = False
    if request.method == 'POST':
        if form.is_valid():
            users_id = form.cleaned_data.get('users')
            role_id = int(form.cleaned_data.get('roles'))
            role = Role.objects.get(id=role_id)
            current_users = team.get_users_in_role(role.name)
            selected_users = [User.objects.get(id=user_id) for user_id in users_id]
            to_remove = list(set(current_users) - set(selected_users))
            to_add = list(set(selected_users) - set(current_users))
            if len(to_remove) == team.get_users_in_role("Admin").count() and len(to_add) == 0 and role.name == "Admin":
                form.add_error('roles', 'Last admin cannot be deleted')
                error = True
            if not error:
                for user in to_add:
                    team.add_user_in_role(user, role.name)
                for user in to_remove:
                    team.remove_user(user)
                return redirect("profiles:user_by_team_list", team_id=team_id)
    breadcrumbs = [
        {'text': 'Teams', 'url': reverse('profiles:team_list')},
        {'text': team.name, 'url': reverse('profiles:user_by_team_list', args=[team_id])},
        {'text': "Users", 'url': ""}
    ]
    context = {'form': form, 'content_type_id': ContentType.objects.get_for_model(Team).id, 'object_id': team.id,
               'breadcrumbs': breadcrumbs}
    return render(request, 'profiles/user_role/user-role-for-object-form.html', context)


@login_required
@permission_required_or_403('profiles.change_team', (Team, 'id', 'team_id'))
def user_in_team_remove(request, team_id, user_id):
    team = get_object_or_404(Team, id=team_id)
    user = User.objects.get(id=user_id)
    if user in team.get_users_in_role("Admin") and team.get_users_in_role("Admin").count() == 1:
        return redirect('profiles:user_by_team_list', team_id=team_id)
    if request.method == 'POST':
        team.remove_user(user)
        return redirect('profiles:user_by_team_list', team_id=team_id)
    args = {
        "team_id": team_id,
        "user_id": user_id
    }
    breadcrumbs = [
        {'text': 'Teams', 'url': reverse('profiles:team_list')},
        {'text': team.name, 'url': reverse('profiles:user_by_team_list', args=[team_id])},
        {'text': "Users", 'url': ""}
    ]
    context = {
        'breadcrumbs': breadcrumbs,
        'confirm_text': mark_safe(f"Confirm to remove the user <strong>{user.username}</strong> from {team}?"),
        'action_url': reverse('profiles:user_in_team_remove', kwargs=args),
        'button_text': 'Remove'
    }
    return render(request, 'generics/confirm-delete-template.html', context=context)
