from Squest.utils.squest_views import *
from resource_tracker_v2.filters.attribute_definition_filter import AttributeDefinitionFilter
from resource_tracker_v2.forms.attribute_definition_form import AttributeDefinitionForm
from resource_tracker_v2.models import AttributeDefinition, ResourceGroup, Transformer
from resource_tracker_v2.tables.attribute_defintion_table import AttributeDefinitionTable


class AttributeDefinitionListView(SquestListView):
    table_class = AttributeDefinitionTable
    model = AttributeDefinition
    filterset_class = AttributeDefinitionFilter


class AttributeDefinitionCreateView(SquestCreateView):
    model = AttributeDefinition
    form_class = AttributeDefinitionForm


class AttributeDefinitionEditView(SquestUpdateView):
    model = AttributeDefinition
    form_class = AttributeDefinitionForm
    pk_url_kwarg = "attribute_definition_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'][0]['url'] = reverse_lazy('resource_tracker_v2:attributedefinition_list')
        return context


class AttributeDefinitionDeleteView(SquestDeleteView):
    model = AttributeDefinition
    pk_url_kwarg = "attribute_definition_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        impacted_resource_group = ResourceGroup.objects.filter(
            id__in=Transformer.objects.filter(
                attribute_definition=kwargs.get("object"))
            .values_list("resource_group__id", flat=True))
        context['breadcrumbs'][0]['url'] = reverse_lazy('resource_tracker_v2:attributedefinition_list')
        context['details'] = {
            'warning_sentence': 'Warning: This attribute is in use by following resource groups:',
            'details_list': [f"{rg}," for rg in impacted_resource_group]
        }
        return context
