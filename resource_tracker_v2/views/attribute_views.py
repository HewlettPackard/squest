from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from resource_tracker_v2.forms.attribute_definition_form import AttributeDefinitionForm
from resource_tracker_v2.models import AttributeDefinition
from resource_tracker_v2.tables.attribute_defintion_table import AttributeDefinitionTable


class AttributeListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_class = AttributeDefinitionTable
    model = AttributeDefinition
    # filterset_class = AttributeDefinitionFilter
    template_name = 'generics/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Attribute definition"
        context['app_name'] = "resource_tracker"
        context['object_name'] = "attribute_definition"
        context['html_button_path'] = "generics/buttons/generic_add_button.html"
        return context


@user_passes_test(lambda u: u.is_superuser)
def attribute_definition_create(request):
    if request.method == 'POST':
        form = AttributeDefinitionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("resource_tracker:attribute_definition_list")
    else:
        form = AttributeDefinitionForm()
    breadcrumbs = [
        {'text': 'Attribute definition', 'url': reverse('resource_tracker:attribute_definition_list')},
        {'text': 'Create a new attribute definition', 'url': ""},
    ]
    context = {'form': form, 'breadcrumbs': breadcrumbs, 'action': 'create'}
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def attribute_definition_edit(request, attribute_definition_id):
    attribute_definition = get_object_or_404(AttributeDefinition, id=attribute_definition_id)
    form = AttributeDefinitionForm(request.POST or None, instance=attribute_definition)
    if form.is_valid():
        form.save()
        return redirect("resource_tracker:attribute_definition_list")
    breadcrumbs = [
        {'text': 'Attribute definition', 'url': reverse('resource_tracker:attribute_definition_list')},
        {'text': attribute_definition.name, 'url': ""},
    ]
    context = {'form': form, 'breadcrumbs': breadcrumbs, 'action': 'edit'}
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def attribute_definition_delete(request, attribute_definition_id):
    attribute_definition = get_object_or_404(AttributeDefinition, id=attribute_definition_id)
    if request.method == 'POST':
        attribute_definition.delete()
        return redirect("resource_tracker:attribute_definition_list")
    breadcrumbs = [
        {'text': 'Attribute definition', 'url': reverse('resource_tracker:attribute_definition_list')},
        {'text': attribute_definition.name, 'url': ""},
    ]
    context = {'attribute_definition': attribute_definition, 'breadcrumbs': breadcrumbs}
    return render(request,
                  'resource_tracking_v2/attributes/attribute-definition-delete.html', context)
