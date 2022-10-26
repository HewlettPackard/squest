from resource_tracker.filters.resource_group_filter import ResourceGroupFilter
from resource_tracker.models import ResourceGroup
from resource_tracker.tables.resource_group_table import ResourceGroupTable
from resource_tracker.views.tag_filter_list_view import TagFilterListView


class ResourceGroupListView(TagFilterListView):
    table_class = ResourceGroupTable
    model = ResourceGroup
    filterset_class = ResourceGroupFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Resource groups"
        context['app_name'] = "resource_tracker"
        context['object_name'] = "resource_group"
        context['html_button_path'] = "generics/buttons/generic_add_button.html"
        return context
