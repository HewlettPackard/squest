from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from resource_tracker_v2.filters.attribute_definition_filter import AttributeDefinitionFilter
from resource_tracker_v2.forms.resource_group_link_form import ResourceGroupLinkForm
from resource_tracker_v2.models import AttributeDefinition, Transformer, ResourceGroup
from resource_tracker_v2.tables.transformer_table import TransformerTable


class ResourceGroupAttributeListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_class = TransformerTable
    # model = AttributeDefinitionLink
    filterset_class = AttributeDefinitionFilter
    template_name = 'generics/list.html'

    def get_table_data(self, **kwargs):
        filtered = super().get_table_data().distinct()
        list_attribute_definition_link = list()
        resource_group_id = self.kwargs.get('resource_group_id')
        resource_group = ResourceGroup.objects.get(id=resource_group_id)
        # get all attribute transformer of this resource group
        transformers = Transformer.objects.filter(source_resource_group__id__in=[resource_group.id]).distinct() & filtered
        return transformers

    def get_context_data(self, **kwargs):
        resource_group_id = self.kwargs.get('resource_group_id')
        resource_group = ResourceGroup.objects.get(id=resource_group_id)
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
            {'text': resource_group.name, 'url': ""},
        ]
        context['title'] = "Resource group attribute"
        context['app_name'] = "resource_tracker"
        context['object_name'] = "resource_group_attribute"
        context['resource_group_id'] = resource_group_id
        context['html_button_path'] = "resource_tracking_v2/resource_group/resource_group_attribute_list_buttons.html"
        return context


@user_passes_test(lambda u: u.is_superuser)
def resource_group_attribute_create(request, resource_group_id):
    resource_group = ResourceGroup.objects.get(id=resource_group_id)
    if request.method == 'POST':
        form = ResourceGroupLinkForm(request.POST, source_resource_group=resource_group)
        if form.is_valid():
            form.save()
            return redirect('resource_tracker:resource_group_attribute_list', resource_group_id)
    else:
        form = ResourceGroupLinkForm(source_resource_group=resource_group)
    args_resource_group = {
        'resource_group_id': resource_group_id
    }
    breadcrumbs = [
        {'text': f"{resource_group.name}", 'url': reverse('resource_tracker:resource_group_attribute_list', kwargs=args_resource_group)},
        {'text': "Add new attribute", 'url': ""}
    ]
    context = {'form': form,
               'breadcrumbs': breadcrumbs,
               'resource_group': resource_group}
    return render(request, 'resource_tracking_v2/resource_group/resource-group-attribute-link.html', context)


@user_passes_test(lambda u: u.is_superuser)
def resource_group_attribute_edit(request, resource_group_id, attribute_id):
    pass


@user_passes_test(lambda u: u.is_superuser)
def resource_group_attribute_delete(request, resource_group_id, attribute_id):
    pass


@user_passes_test(lambda u: u.is_superuser)
def ajax_load_attribute(request):
    current_resource_group_id = request.GET.get('current_resource_group_id')
    target_resource_group_id = request.GET.get('target_resource_group_id')
    current_resource_group = ResourceGroup.objects.get(id=current_resource_group_id)
    target_resource_group = ResourceGroup.objects.get(id=target_resource_group_id)
    all_available_attribute_to_target_rg = target_resource_group.attribute_definitions.all()
    already_linked = Transformer.objects.filter(destination_resource_group=target_resource_group,
                                                source_resource_group=current_resource_group)
    # exclude already linked
    all_available_attribute_to_target_rg = all_available_attribute_to_target_rg.exclude(id__in=[transformer.destination_attribute_definition.id for transformer in already_linked])

    options = [(attribute.id, attribute.name) for attribute in all_available_attribute_to_target_rg.all()]
    return render(request, 'service_catalog/settings/global_hooks/state-dropdown-list-option.html',
                  {'options': options})
