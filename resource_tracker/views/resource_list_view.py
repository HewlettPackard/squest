from django.urls import reverse
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from guardian.mixins import LoginRequiredMixin

from resource_tracker.filters.resource_filter import ResourceFilter
from resource_tracker.models import Resource
from resource_tracker.tables.resource_table import ResourceTable


class ResourceListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = ResourceTable
    model = Resource
    template_name = 'generics/list.html'
    filterset_class = ResourceFilter

    def get_table_data(self, **kwargs):
        filtered = super().get_table_data().distinct()
        return Resource.objects.filter(resource_group_id=self.kwargs.get('resource_group_id')).distinct() & filtered

    def get_context_data(self, **kwargs):
        resource_group_id = self.kwargs.get('resource_group_id')
        context = super().get_context_data(**kwargs)
        context['resource_group_id'] = resource_group_id
        context['title'] = "Resources"
        context['action_url'] = reverse('resource_tracker:resource_group_resource_bulk_delete_confirm',
                                        kwargs={'resource_group_id': resource_group_id})
        context['html_button_path'] = "resource_tracking/resource_group/resources/resource_list_buttons.html"
        return context
