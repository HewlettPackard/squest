from django.urls import reverse

from resource_tracker.filters.resource_filter import ResourceFilter
from resource_tracker.models import Resource, ResourceGroup
from resource_tracker.tables.resource_table import ResourceTable
from resource_tracker.views import TagFilterListView


class ResourceListView(TagFilterListView):
    table_class = ResourceTable
    model = Resource
    filterset_class = ResourceFilter

    def get_table_data(self, **kwargs):
        filtered = super().get_table_data().distinct()
        return Resource.objects.filter(resource_group_id=self.kwargs.get('resource_group_id')).distinct() & filtered

    def get_context_data(self, **kwargs):
        resource_group_id = self.kwargs.get('resource_group_id')
        resource_group = ResourceGroup.objects.get(id=resource_group_id)
        context = super().get_context_data(**kwargs)
        context['resource_group_id'] = resource_group_id
        context['breadcrumbs'] = [
            {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
            {'text': resource_group.name, 'url': ""}
        ]
        context['action_url'] = reverse('resource_tracker:resource_group_resource_bulk_delete_confirm',
                                        kwargs={'resource_group_id': resource_group_id})
        context['html_button_path'] = "resource_tracking/resource_group/resources/resource_list_buttons.html"
        return context
