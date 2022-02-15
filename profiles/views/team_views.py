from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe
from guardian.decorators import permission_required_or_403
from profiles.forms import TeamForm, UserRoleForObjectForm, CreateTeamRoleBindingForObjectForm
from profiles.models import Role, TeamRoleBinding
from profiles.models.team import Team
from profiles.tables import UserByObjectTable, RoleBindingByTeamTable
from profiles.views import get_roles_from_content_type, get_objects_of_user_from_content_type


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
                    team.remove_user_in_role(user, role.name)
                return redirect("profiles:team_details", team_id=team_id)
    breadcrumbs = [
        {'text': 'Teams', 'url': reverse('profiles:team_list')},
        {'text': team.name, 'url': reverse('profiles:team_details', args=[team_id])},
        {'text': "Users", 'url': ""}
    ]
    context = {'form': form, 'content_type_id': ContentType.objects.get_for_model(Team).id, 'object_id': team.id,
               'breadcrumbs': breadcrumbs}
    return render(request, 'profiles/role/user-role-for-object-form.html', context)


@login_required
@permission_required_or_403('profiles.change_team', (Team, 'id', 'team_id'))
def user_in_team_remove(request, team_id, user_id):
    team = get_object_or_404(Team, id=team_id)
    user = User.objects.get(id=user_id)
    if user in team.get_users_in_role("Admin") and team.get_users_in_role("Admin").count() == 1:
        return redirect('profiles:team_details', team_id=team_id)
    if request.method == 'POST':
        team.remove_user_in_role(user)
        return redirect('profiles:team_details', team_id=team_id)
    args = {
        "team_id": team_id,
        "user_id": user_id
    }
    breadcrumbs = [
        {'text': 'Teams', 'url': reverse('profiles:team_list')},
        {'text': team.name, 'url': reverse('profiles:team_details', args=[team_id])},
        {'text': "Users", 'url': ""}
    ]
    context = {
        'breadcrumbs': breadcrumbs,
        'confirm_text': mark_safe(f"Confirm to remove the user <strong>{user.username}</strong> from {team}?"),
        'action_url': reverse('profiles:user_in_team_remove', kwargs=args),
        'button_text': 'Remove'
    }
    return render(request, 'generics/confirm-delete-template.html', context=context)


@login_required
@permission_required_or_403('profiles.view_team', (Team, 'id', 'team_id'))
def team_details(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    bindings = TeamRoleBinding.objects.filter(team=team)
    users_table = UserByObjectTable(team.get_all_users())
    roles_table = RoleBindingByTeamTable(bindings)
    context = {
        'breadcrumbs': [
            {'text': 'Teams', 'url': reverse('profiles:team_list')},
            {'text': Team.objects.get(id=team_id).name, 'url': ""}
        ],
        'roles': team.get_roles_of_users(),
        'html_button_path': "profiles/role/change-users-in-role.html",
        'app_name': 'profiles',
        'object_name': 'team',
        'object': team,
        'group_id': team_id,
        'object_id': team_id,
        'parent_id': team_id,
        'users_table': users_table,
        'roles_table': roles_table
    }
    return render(request, 'profiles/team-details.html', context=context)


@login_required
@permission_required_or_403('profiles.change_team', (Team, 'id', 'team_id'))
def team_role_binding_create(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    content_types = list()
    for role in Role.objects.all():
        ct_tuple = (role.content_type.id, role.content_type.name)
        if ct_tuple not in content_types:
            content_types.append(ct_tuple)
    form = CreateTeamRoleBindingForObjectForm(
        request.POST or None,
        user=request.user,
        content_type=content_types
    )
    if request.method == 'POST':
        if form.is_valid():
            content_type = ContentType.objects.get(id=form.cleaned_data.get('content_type'))
            role = Role.objects.get(id=form.cleaned_data.get('role'))
            object_id = form.cleaned_data.get('object')
            TeamRoleBinding.objects.create(team=team, content_type=content_type, role=role, object_id=object_id)
            return redirect(reverse("profiles:team_details", args=[team_id]) + "#roles")
    breadcrumbs = [
        {'text': 'Teams', 'url': reverse('profiles:team_list')},
        {'text': team.name, 'url': reverse('profiles:team_details', args=[team_id])},
        {'text': "Roles", 'url': ""}
    ]
    context = {'form': form, 'breadcrumbs': breadcrumbs}
    return render(request, 'profiles/role/create-team-role-binding-for-object-form.html', context)


@login_required
@permission_required_or_403('profiles.change_team', (Team, 'id', 'team_id'))
def team_role_binding_delete(request, team_id, team_role_binding_id):
    team = get_object_or_404(Team, id=team_id)
    team_role_binding = get_object_or_404(TeamRoleBinding, id=team_role_binding_id)
    if request.method == 'POST':
        team_role_binding.delete()
        return redirect(reverse("profiles:team_details", args=[team_id]) + "#roles")
    context = {
        'breadcrumbs': [
            {'text': "Teams", 'url': reverse('profiles:team_list')},
            {'text': team.name, 'url': reverse('profiles:team_details', args=[team.id])},
        ],
        'confirm_text': mark_safe(f"Confirm deletion of <strong>{team_role_binding.role.name}</strong> role for the "
                                  f"team <strong>{team.name}</strong> on the {team_role_binding.content_type.name} "
                                  f"<strong>{team_role_binding.content_object}</strong>?"),
        'action_url': reverse('profiles:team_role_binding_delete',
                              kwargs={'team_id': team_id, 'team_role_binding_id': team_role_binding_id}),
        'button_text': 'Delete',
        'object_name': "team_role_binding"
    }
    return render(request, 'generics/confirm-delete-template.html', context=context)



@login_required
def ajax_team_role_binding_form_update_roles(request):
    content_type_id = request.GET.get('content_type_id')
    return render(request, 'profiles/role/object-dropdown-list.html',
                  {'objects': get_roles_from_content_type(content_type_id)})


@login_required
def ajax_team_role_binding_form_update_objects(request):
    content_type_id = request.GET.get('content_type_id')
    return render(request, 'profiles/role/object-dropdown-list.html',
                  {'objects': get_objects_of_user_from_content_type(request.user, content_type_id)})

