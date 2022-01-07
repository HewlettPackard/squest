from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from guardian.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe

from profiles.filters.quota_attribute_definition_filter import QuotaAttributeDefinitionFilter
from profiles.forms.quota_attribute_definition_form import QuotaAttributeDefinitionForm
from profiles.models import QuotaAttributeDefinition
from profiles.tables.quota_attribute_definition_table import QuotaAttributeDefinitionTable


@method_decorator(login_required, name='dispatch')
class QuotaAttributeDefinitionListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = QuotaAttributeDefinitionTable
    model = QuotaAttributeDefinition
    template_name = 'generics/list.html'
    filterset_class = QuotaAttributeDefinitionFilter

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied
        return super(QuotaAttributeDefinitionListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = "Quota attributes"
        context['html_button_path'] = "generics/buttons/generic_add_button.html"
        context['app_name'] = "profiles"
        context['object_name'] = "quota_attribute_definition"
        return context


@user_passes_test(lambda u: u.is_superuser)
def quota_attribute_definition_edit(request, quota_attribute_definition_id):
    quota_attribute_definition = get_object_or_404(QuotaAttributeDefinition, id=quota_attribute_definition_id)
    form = QuotaAttributeDefinitionForm(request.POST or None, instance=quota_attribute_definition)
    if form.is_valid():
        form.save()
        return redirect("profiles:quota_attribute_definition_list")
    breadcrumbs = [
        {'text': 'Quota attributes', 'url': reverse('profiles:quota_attribute_definition_list')},
        {'text': quota_attribute_definition.name, 'url': ""},
    ]
    context = {'form': form, 'quota_attribute_definition': quota_attribute_definition,
               'object_name': "quota_attribute_definition", 'breadcrumbs': breadcrumbs, 'action': "edit"}
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def quota_attribute_definition_create(request):
    if request.method == 'POST':
        form = QuotaAttributeDefinitionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("profiles:quota_attribute_definition_list")
    else:
        form = QuotaAttributeDefinitionForm()
    breadcrumbs = [
        {'text': 'Quota attributes', 'url': reverse('profiles:quota_attribute_definition_list')},
        {'text': 'Create a new quota attribute', 'url': ""},
    ]
    context = {'form': form, 'object_name': "quota_attribute_definition", 'breadcrumbs': breadcrumbs,
               'action': "create"}
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def quota_attribute_definition_delete(request, quota_attribute_definition_id):
    quota_attribute_definition = get_object_or_404(QuotaAttributeDefinition, id=quota_attribute_definition_id)
    if request.method == 'POST':
        quota_attribute_definition.delete()
        return redirect("profiles:quota_attribute_definition_list")
    args = {
        "quota_attribute_definition_id": quota_attribute_definition_id,
    }
    breadcrumbs = [
        {'text': 'Quota attributes', 'url': reverse('profiles:quota_attribute_definition_list')},
        {'text': quota_attribute_definition.name, 'url': ""}
    ]
    context = {
        'breadcrumbs': breadcrumbs,
        'confirm_text': mark_safe(f"Confirm deletion of <strong>{quota_attribute_definition.name}</strong>?"),
        'action_url': reverse('profiles:quota_attribute_definition_delete', kwargs=args),
        'button_text': 'Delete',
        'details': {'warning_sentence': 'This quota attribute was linked to the following billing groups:',
                    'details_list': [binding.billing_group.name for binding in
                                     quota_attribute_definition.quota_bindings.all()]} if
        quota_attribute_definition.attribute_definitions.all() else None,
        'object_name': "quota_attribute_definition"
    }
    return render(request, 'generics/confirm-delete-template.html', context=context)
