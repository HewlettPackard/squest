from Squest.utils.squest_views import *
from resource_tracker_v2.filters.resource_group_filter import ResourceGroupFilter
from resource_tracker_v2.forms.resource_group_form import ResourceGroupForm
from resource_tracker_v2.models import ResourceGroup, AttributeDefinition, Transformer
from resource_tracker_v2.tables.resource_group_table import ResourceGroupTable


class ResourceGroupListView(SquestListView):
    model = ResourceGroup
    filterset_class = ResourceGroupFilter
    table_class = ResourceGroupTable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['extra_html_button_path'] = "resource_tracking_v2/resource_group/button_switch_csv.html"
        return context


class ResourceGroupCreateView(SquestCreateView):
    model = ResourceGroup
    form_class = ResourceGroupForm


class ResourceGroupEditView(SquestUpdateView):
    model = ResourceGroup
    form_class = ResourceGroupForm
    pk_url_kwarg = "resource_group_id"


class ResourceGroupDeleteView(SquestDeleteView):
    model = ResourceGroup
    pk_url_kwarg = "resource_group_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['details'] = {
            'warning_sentence': 'Warning: This resource group is in use by following resource:',
            'details_list': [f"{resource}," for resource in self.get_object().resources.all()]
        }
        return context


class ResourceGroupListViewCSV(SquestListView):
    model = ResourceGroup
    filterset_class = ResourceGroupFilter
    table_class = ResourceGroupTable
    template_name = 'resource_tracking_v2/resource_group/csv.html'

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
        context['extra_html_button_path'] = "resource_tracking_v2/resource_group/button_switch_table.html"

        return context
