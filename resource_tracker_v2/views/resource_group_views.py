from Squest.utils.squest_views import *
from resource_tracker_v2.filters.resource_group_filter import ResourceGroupFilter
from resource_tracker_v2.forms.resource_group_form import ResourceGroupForm
from resource_tracker_v2.models import ResourceGroup, AttributeDefinition, Transformer
from resource_tracker_v2.tables.resource_group_table import ResourceGroupTable
from resource_tracker_v2.tables.resource_table import ResourceTable
from resource_tracker_v2.tables.transformer_table import TransformerTable


class ResourceGroupListView(SquestListView):
    model = ResourceGroup
    filterset_class = ResourceGroupFilter
    table_class = ResourceGroupTable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['extra_html_button_path'] = "resource_tracker_v2/resource_group/button_switch_csv.html"
        return context


class ResourceGroupDetailView(SquestDetailView):
    model = ResourceGroup

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attributes_table"] = TransformerTable(self.object.transformers.all())
        context["resources_table"] = ResourceTable(self.object.resources.all(), hide_fields=('selection',))
        return context


class ResourceGroupCreateView(SquestCreateView):
    model = ResourceGroup
    form_class = ResourceGroupForm
    form_class = ResourceGroupForm


class ResourceGroupEditView(SquestUpdateView):
    model = ResourceGroup
    form_class = ResourceGroupForm


class ResourceGroupDeleteView(SquestDeleteView):
    model = ResourceGroup


class ResourceGroupListViewCSV(SquestListView):
    model = ResourceGroup
    filterset_class = ResourceGroupFilter
    table_class = ResourceGroupTable
    template_name = 'resource_tracker_v2/resource_group/csv.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        list_attribute_name = AttributeDefinition.objects.values_list("name", flat=True)
        transformer_values = Transformer.objects.values("resource_group__name", "attribute_definition__name",
                                                        "total_produced", "total_consumed", "factor")

        data_dict = dict()

        for transformer_value in transformer_values:
            rg_name = transformer_value["resource_group__name"]
            if rg_name not in data_dict:
                data_dict[rg_name] = dict()
            transformer_attribute = transformer_value["attribute_definition__name"]
            for attribute in list_attribute_name:
                if attribute not in data_dict[rg_name]:
                    data_dict[rg_name][attribute] = {
                        "produced": "",
                        "consumed": "",
                        "available": "",
                        "factor": "",
                    }

                if attribute == transformer_attribute:
                    data_dict[rg_name][attribute] = {
                        "produced": transformer_value["total_produced"],
                        "consumed": transformer_value["total_consumed"],
                        "available": transformer_value["total_produced"] - transformer_value["total_consumed"],
                        "factor": transformer_value["factor"],
                    }

        context['data'] = data_dict
        context['list_attribute_name'] = list_attribute_name
        context['extra_html_button_path'] = "resource_tracker_v2/resource_group/button_switch_table.html"

        return context
