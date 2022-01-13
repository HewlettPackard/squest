from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from guardian.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe

from profiles.filters.quota_filter import QuotaFilter
from profiles.forms.quota_form import QuotaForm
from profiles.models import Quota
from profiles.tables.quota_table import QuotaTable


@method_decorator(login_required, name='dispatch')
class QuotaListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = QuotaTable
    model = Quota
    template_name = 'generics/list.html'
    filterset_class = QuotaFilter

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied
        return super(QuotaListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = "Quota attributes"
        context['html_button_path'] = "generics/buttons/generic_add_button.html"
        context['app_name'] = "profiles"
        context['object_name'] = "quota"
        return context


@user_passes_test(lambda u: u.is_superuser)
def quota_edit(request, quota_id):
    quota = get_object_or_404(Quota, id=quota_id)
    form = QuotaForm(request.POST or None, instance=quota)
    if form.is_valid():
        form.save()
        return redirect("profiles:quota_list")
    breadcrumbs = [
        {'text': 'Quota attributes', 'url': reverse('profiles:quota_list')},
        {'text': quota.name, 'url': ""},
    ]
    context = {'form': form, 'quota': quota,
               'object_name': "quota", 'breadcrumbs': breadcrumbs, 'action': "edit"}
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def quota_create(request):
    if request.method == 'POST':
        form = QuotaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("profiles:quota_list")
    else:
        form = QuotaForm()
    breadcrumbs = [
        {'text': 'Quota attributes', 'url': reverse('profiles:quota_list')},
        {'text': 'Create a new quota attribute', 'url': ""},
    ]
    context = {'form': form, 'object_name': "quota", 'breadcrumbs': breadcrumbs,
               'action': "create"}
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def quota_delete(request, quota_id):
    quota = get_object_or_404(Quota, id=quota_id)
    if request.method == 'POST':
        quota.delete()
        return redirect("profiles:quota_list")
    args = {
        "quota_id": quota_id,
    }
    breadcrumbs = [
        {'text': 'Quota attributes', 'url': reverse('profiles:quota_list')},
        {'text': quota.name, 'url': ""}
    ]
    context = {
        'breadcrumbs': breadcrumbs,
        'confirm_text': mark_safe(f"Confirm deletion of <strong>{quota.name}</strong>?"),
        'action_url': reverse('profiles:quota_delete', kwargs=args),
        'button_text': 'Delete',
        'details': {'warning_sentence': 'This quota attribute was linked to the following billing groups:',
                    'details_list': [binding.billing_group.name for binding in
                                     quota.quota_bindings.all()]} if
        quota.attribute_definitions.all() else None,
        'object_name': "quota"
    }
    return render(request, 'generics/confirm-delete-template.html', context=context)
