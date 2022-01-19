from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group, User
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe

from profiles.forms import GroupForm, AddUserForm


@user_passes_test(lambda u: u.is_superuser)
def group_edit(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    form = GroupForm(request.POST or None, instance=group)
    if form.is_valid():
        form.save()
        return redirect("profiles:group_list")
    breadcrumbs = [
        {'text': 'Groups', 'url': reverse('profiles:group_list')},
        {'text': group.name, 'url': ""},
    ]
    context = {'form': form, 'group': group, 'object_name': "group", 'breadcrumbs': breadcrumbs}
    return render(request, 'profiles/group/group-edit.html', context)


@user_passes_test(lambda u: u.is_superuser)
def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("profiles:group_list")
    else:
        form = GroupForm()
    breadcrumbs = [
        {'text': 'Groups', 'url': reverse('profiles:group_list')},
        {'text': 'Create a new group', 'url': ""},
    ]
    context = {'form': form, 'object_name': "group", 'breadcrumbs': breadcrumbs}
    return render(request, 'profiles/group/group-create.html', context)


@user_passes_test(lambda u: u.is_superuser)
def group_delete(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.method == 'POST':
        group.delete()
        return redirect("profiles:group_list")
    args = {
        "group_id": group_id,
    }
    breadcrumbs = [
        {'text': 'Groups', 'url': reverse('profiles:group_list')},
        {'text': group.name, 'url': ""}
    ]
    context = {
        'breadcrumbs': breadcrumbs,
        'confirm_text': mark_safe(f"Confirm deletion of <strong>{group.name}</strong>?"),
        'action_url': reverse('profiles:group_delete', kwargs=args),
        'button_text': 'Delete',
        'details': {'warning_sentence': 'Warning: some users are still present in this group:',
                    'details_list': [user.username for user in group.user_set.all()]
                    } if group.user_set.all() else None,
        'object_name': "group"
    }
    return render(request, 'generics/confirm-delete-template.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def user_in_group_update(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    form = AddUserForm(request.POST or None, group=group)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect("profiles:user_by_group_list", group_id=group_id)
    breadcrumbs = [
        {'text': 'Groups', 'url': reverse('profiles:group_list')},
        {'text': group.name, 'url': reverse('profiles:user_by_group_list', args=[group_id])},
        {'text': "Users", 'url': ""}
    ]
    context = {'form': form, 'group': group, 'object_name': "group", 'breadcrumbs': breadcrumbs}
    return render(request, 'profiles/group/user-in-group-update.html', context)


@user_passes_test(lambda u: u.is_superuser)
def user_in_group_remove(request, group_id, user_id):
    group = get_object_or_404(Group, id=group_id)
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        group.user_set.remove(user)
        return redirect('profiles:user_by_group_list', group_id=group_id)
    args = {
        "group_id": group_id,
        "user_id": user_id
    }
    breadcrumbs = [
        {'text': 'Groups', 'url': reverse('profiles:group_list')},
        {'text': group.name, 'url': reverse('profiles:user_by_group_list', args=[group_id])},
        {'text': "Users", 'url': ""}
    ]
    context = {
        'breadcrumbs': breadcrumbs,
        'confirm_text': mark_safe(f"Confirm to remove the user <strong>{user.username}</strong> from {group}?"),
        'action_url': reverse('profiles:user_in_group_remove', kwargs=args),
        'button_text': 'Remove'
    }
    return render(request, 'generics/confirm-delete-template.html', context=context)
