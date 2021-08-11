from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group, User
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe

from profiles.forms import GroupForm, AddUserForm


@user_passes_test(lambda u: u.is_superuser)
def group_list(request):
    groups = Group.objects.all()
    breadcrumbs = [
        {'text': 'Groups', 'url': ''},
    ]
    context = {'groups': groups, 'group_url': "group", 'breadcrumbs': breadcrumbs}
    return render(request, 'profiles/group/group-list.html', context)


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
    template = {'form': {'button': 'edit'}}
    context = {'form': form, 'group': group, 'group_url': "group", 'breadcrumbs': breadcrumbs, 'template': template}
    return render(request, 'generics/create_page.html', context)


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
    template = {'form': {'button': 'create'}}
    context = {'form': form, 'group_url': "group", 'breadcrumbs': breadcrumbs, 'template': template}
    return render(request, 'generics/create_page.html', context)


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
    template_form = {'confirm_text': mark_safe(f"Confirm deletion of <strong>{group.name}</strong>?"),
                     'button_text': 'Delete',
                     'details': {
                         'warning_sentence': 'Warning: some users are still present in this group, see them below:',
                         'details_list': [user.username for user in group.user_set.all()]
                         } if group.user_set.all() else None }
    context = {
        'breadcrumbs': breadcrumbs,
        'template_form':template_form,
        'group_url': "group"
    }
    return render(request, 'generics/confirm-delete-template.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def user_by_group_list(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    breadcrumbs = [
        {'text': 'Groups', 'url': reverse('profiles:group_list')},
        {'text': group.name, 'url': ""},
        {'text': "Users", 'url': ""}
    ]
    context = {'group': group, 'group_url': "group", 'breadcrumbs': breadcrumbs}
    return render(request, 'profiles/group/user-by-group-list.html', context)


@user_passes_test(lambda u: u.is_superuser)
def user_in_group_update(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    form = AddUserForm(request.POST or None, current_users=group.user_set.all())
    if request.method == 'POST':
        if form.is_valid():
            users_id = form.cleaned_data.get('users')
            current_users = group.user_set.all()
            selected_users = [User.objects.get(id=user_id) for user_id in users_id]
            to_remove = list(set(current_users) - set(selected_users))
            to_add = list(set(selected_users) - set(current_users))
            for user in to_remove:
                group.user_set.remove(user)
            for user in to_add:
                group.user_set.add(user)
            return redirect("profiles:user_by_group_list", group_id=group_id)
    breadcrumbs = [
        {'text': 'Groups', 'url': reverse('profiles:group_list')},
        {'text': group.name, 'url': reverse('profiles:user_by_group_list', args=[group_id])},
        {'text': "Users", 'url': ""}
    ]
    template = {'form': {'button': 'edit'}}
    context = {'form': form, 'group': group, 'group_url': "group", 'breadcrumbs': breadcrumbs, 'template': template}
    return render(request, 'generics/create_page.html', context)


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
    template_form = {
        'confirm_text': mark_safe(f"Confirm to remove the user <strong>{user.username}</strong> from {group}?"),
        'button_text': 'Remove'
    }
    context = {
        'breadcrumbs': breadcrumbs,
        'template_form': template_form
    }
    return render(request, 'generics/confirm-delete-template.html', context=context)
