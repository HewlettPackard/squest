from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe

from profiles.filters.billing_group_filter import BillingGroupFilter
from profiles.forms import AddUserForm
from profiles.forms.billing_group_forms import BillingGroupForm
from profiles.models.billing_group import BillingGroup
from profiles.tables.quota_binding_table import QuotaBindingTable
from profiles.tables.user_by_billing_group_table import UserByBillingGroupTable


@user_passes_test(lambda u: u.is_superuser)
def billing_group_edit(request, billing_group_id):
    group = get_object_or_404(BillingGroup, id=billing_group_id)
    form = BillingGroupForm(request.POST or None, instance=group)
    if form.is_valid():
        form.save()
        return redirect("profiles:billing_group_list")
    breadcrumbs = [
        {'text': 'Billing groups', 'url': reverse('profiles:billing_group_list')},
        {'text': group.name, 'url': reverse("profiles:billing_group_list") + f"?id={billing_group_id}#quota{billing_group_id}"},
    ]
    context = {'form': form, 'group': group, 'object_name': "billing_group", 'breadcrumbs': breadcrumbs}
    return render(request, 'profiles/group/group-edit.html', context)


@user_passes_test(lambda u: u.is_superuser)
def billing_group_create(request):
    if request.method == 'POST':
        form = BillingGroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("profiles:billing_group_list")
    else:
        form = BillingGroupForm()
    breadcrumbs = [
        {'text': 'Billing groups', 'url': reverse('profiles:billing_group_list')},
        {'text': 'Create a new billing group', 'url': ""},
    ]
    context = {'form': form, 'object_name': "billing_group", 'breadcrumbs': breadcrumbs}
    return render(request, 'profiles/group/group-create.html', context)


@user_passes_test(lambda u: u.is_superuser)
def billing_group_delete(request, billing_group_id):
    group = get_object_or_404(BillingGroup, id=billing_group_id)
    if request.method == 'POST':
        group.delete()
        return redirect("profiles:billing_group_list")
    args = {
        "billing_group_id": billing_group_id,
    }
    breadcrumbs = [
        {'text': 'Billing groups', 'url': reverse('profiles:billing_group_list')},
        {'text': group.name, 'url': reverse("profiles:billing_group_list") + f"?id={billing_group_id}#quota{billing_group_id}"}
    ]
    context = {
        'breadcrumbs': breadcrumbs,
        'confirm_text': mark_safe(f"Confirm deletion of <strong>{group.name}</strong>?"),
        'action_url': reverse('profiles:billing_group_delete', kwargs=args),
        'button_text': 'Delete',
        'details': {'warning_sentence': 'Warning: some users are still present in this group:',
                    'details_list': [user.username for user in group.user_set.all()]
                    } if group.user_set.all() else None
    }
    return render(request, 'generics/confirm-delete-template.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def user_in_billing_group_update(request, billing_group_id):
    group = get_object_or_404(BillingGroup, id=billing_group_id)
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

            return redirect(reverse("profiles:billing_group_list") + f"?id={billing_group_id}#quota{billing_group_id}")
    breadcrumbs = [
        {'text': 'Billing groups', 'url': reverse('profiles:billing_group_list')},
        {'text': group.name, 'url': reverse("profiles:billing_group_list") + f"?id={billing_group_id}#quota{billing_group_id}"},
        {'text': "Users", 'url': ""}
    ]
    context = {'form': form, 'group': group, 'object_name': "billing_group", 'breadcrumbs': breadcrumbs}
    return render(request, 'profiles/group/user-in-group-update.html', context)


@user_passes_test(lambda u: u.is_superuser)
def user_in_billing_group_remove(request, billing_group_id, user_id):
    group = get_object_or_404(BillingGroup, id=billing_group_id)
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        group.user_set.remove(user)
        return redirect(reverse("profiles:billing_group_list") + f"?id={billing_group_id}#quota{billing_group_id}")
    args = {
        "billing_group_id": billing_group_id,
        "user_id": user_id
    }
    breadcrumbs = [
        {'text': 'Billing groups', 'url': reverse('profiles:billing_group_list')},
        {'text': group.name, 'url': reverse("profiles:billing_group_list") + f"?id={billing_group_id}#quota{billing_group_id}"},
        {'text': "Users", 'url': ""}
    ]
    context = {
        'breadcrumbs': breadcrumbs,
        'confirm_text': mark_safe(f"Confirm to remove the user <strong>{user.username}</strong> from {group}?"),
        'action_url': reverse('profiles:user_in_billing_group_remove', kwargs=args),
        'button_text': 'Remove'
    }
    return render(request, 'generics/confirm-delete-template.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def billing_group_list(request):
    billing_filtered = BillingGroupFilter(request.GET, queryset=BillingGroup.objects.all())

    tables_dict = dict()
    for billing_group in billing_filtered.queryset.all():
        tables = dict()
        tables['users_table'] = UserByBillingGroupTable(billing_group.user_set.all())
        tables['quota_table'] = QuotaBindingTable(billing_group.quota_bindings.all())
        tables_dict[billing_group.id] = tables
    context = {
        'title': 'Billing Groups',
        'app_name': 'profiles',
        'object_name': 'billing_group',
        'billing_groups': billing_filtered,
        'tables_dict': tables_dict,
        'current_tab': 'users'
    }
    return render(request, 'profiles/billing-group-details-list.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def billing_group_refresh_quota(request, billing_group_id):
    group = get_object_or_404(BillingGroup, id=billing_group_id)
    group.update_quota()
    return redirect(request.META['HTTP_REFERER'])
