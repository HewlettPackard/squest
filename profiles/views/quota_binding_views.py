from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe
from profiles.forms.quota_binding_limit_form import QuotaBindingLimitForm
from profiles.models.billing_group import BillingGroup
from profiles.forms.manage_quota_binding_form import ManageQuotaBindingForm
from profiles.forms.quota_binding_form import QuotaBindingForm


@user_passes_test(lambda u: u.is_superuser)
def quota_binding_edit(request, billing_group_id, quota_binding_id):
    billing_group = get_object_or_404(BillingGroup, id=billing_group_id)
    quota_binding = get_object_or_404(billing_group.quota_bindings.all(), id=quota_binding_id)
    form = QuotaBindingForm(request.POST or None, instance=quota_binding)
    if form.is_valid():
        form.save()
        return redirect(reverse("profiles:billing_group_list") + f"?id={billing_group.id}#quota{billing_group.id}")
    breadcrumbs = [
        {'text': 'Billing Groups', 'url': reverse('profiles:billing_group_list')},
        {'text': billing_group.name,
         'url': reverse("profiles:billing_group_list") + f"?id={billing_group.id}#quota{billing_group.id}"},
        {'text': quota_binding.quota.name, 'url': ""},
    ]
    context = {'form': form, 'billing_group': billing_group, 'object_name': "billing_group", 'breadcrumbs': breadcrumbs,
               'action': "edit"}
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def quota_binding_delete(request, billing_group_id, quota_binding_id):
    billing_group = get_object_or_404(BillingGroup, id=billing_group_id)
    quota_binding = get_object_or_404(billing_group.quota_bindings.all(), id=quota_binding_id)
    if request.method == 'POST':
        quota_binding.delete()
        return redirect(reverse("profiles:billing_group_list") + f"?id={billing_group.id}#quota{billing_group.id}")
    args = {
        "billing_group_id": billing_group_id,
        "quota_binding_id": quota_binding_id,
    }
    breadcrumbs = [
        {'text': 'Billing Groups', 'url': reverse('profiles:billing_group_list')},
        {'text': billing_group.name,
         'url': reverse("profiles:billing_group_list") + f"?id={billing_group.id}#quota{billing_group.id}"},
        {'text': quota_binding.quota.name, 'url': ""},
    ]
    context = {
        'breadcrumbs': breadcrumbs,
        'confirm_text': mark_safe(
            f"Confirm deletion of <strong>{quota_binding.quota.name}</strong> in {billing_group.name}?"),
        'action_url': reverse('profiles:quota_binding_delete', kwargs=args),
        'button_text': 'Delete',
        'details': None,
        'object_name': "billing_group"
    }
    return render(request, 'generics/confirm-delete-template.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def quota_binding_edit_all(request, billing_group_id):
    billing_group = get_object_or_404(BillingGroup, id=billing_group_id)
    form = ManageQuotaBindingForm(request.POST or None, billing_group=billing_group)
    if form.is_valid():
        form.save()
        return redirect("profiles:quota_binding_set_limits", billing_group_id=billing_group_id)
    breadcrumbs = [
        {'text': 'Billing Groups', 'url': reverse('profiles:billing_group_list')},
        {'text': billing_group.name,
         'url': reverse("profiles:billing_group_list") + f"?id={billing_group.id}#quota{billing_group.id}"},
    ]
    context = {'form': form, 'billing_group': billing_group, 'object_name': "billing_group", 'breadcrumbs': breadcrumbs,
               'icon_button': 'fas fa-arrow-circle-right', 'text_button': 'Set limits',  'color_button': 'primary'}
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def quota_binding_set_limits(request, billing_group_id):
    billing_group = get_object_or_404(BillingGroup, id=billing_group_id)
    form = QuotaBindingLimitForm(request.POST or None, billing_group=billing_group)
    if form.is_valid():
        form.save()
        return redirect(reverse("profiles:billing_group_list") + f"?id={billing_group.id}#quota{billing_group.id}")
    breadcrumbs = [
        {'text': 'Billing Groups', 'url': reverse('profiles:billing_group_list')},
        {'text': billing_group.name,
         'url': reverse("profiles:billing_group_list") + f"?id={billing_group.id}#quota{billing_group.id}"},
    ]
    context = {'form': form, 'billing_group': billing_group, 'object_name': "billing_group", 'breadcrumbs': breadcrumbs,
               'action': "edit"}
    return render(request, 'generics/generic_form.html', context)
