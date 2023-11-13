from Squest.utils.squest_views import *
from resource_tracker_v2.filters.attribute_group_filter import AttributeGroupFilter
from resource_tracker_v2.forms.attribute_group_form import AttributeGroupForm
from resource_tracker_v2.models import AttributeGroup
from resource_tracker_v2.tables.attribute_definition_table import AttributeDefinitionTable
from resource_tracker_v2.tables.attribute_group_table import AttributeGroupTable


class AttributeGroupDetailView(SquestDetailView):
    model = AttributeGroup

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attributes'] = AttributeDefinitionTable(
            self.object.attribute_definitions.all(),
            hide_fields=["attribute_group", "actions"]
        )

        context['breadcrumbs'] = [
            {
                'text': self.django_content_type.name.capitalize(),
                'url': self.get_generic_url('list')
            },
            {
                'text': self.get_object().name,
                'url': ""
            },
        ]
        return context


class AttributeGroupListView(SquestListView):
    table_class = AttributeGroupTable
    model = AttributeGroup
    filterset_class = AttributeGroupFilter


class AttributeGroupCreateView(SquestCreateView):
    model = AttributeGroup
    form_class = AttributeGroupForm


class AttributeGroupEditView(SquestUpdateView):
    model = AttributeGroup
    form_class = AttributeGroupForm


class AttributeGroupDeleteView(SquestDeleteView):
    model = AttributeGroup
