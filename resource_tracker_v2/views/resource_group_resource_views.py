from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from resource_tracker.views import TagFilterListView
from resource_tracker_v2.filters.resource_filter import ResourceFilter
from resource_tracker_v2.forms.resource_form import ResourceForm
from resource_tracker_v2.models import Resource, ResourceGroup
from resource_tracker_v2.tables.resource_table import ResourceTable


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
        # context['action_url'] = reverse('resource_tracker:resource_group_resource_bulk_delete_confirm',
        #                                 kwargs={'resource_group_id': resource_group_id})
        context['html_button_path'] = "resource_tracking_v2/resource_group/resources/resource_list_buttons.html"
        return context


@user_passes_test(lambda u: u.is_superuser)
def resource_group_resource_create(request, resource_group_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    parameters = {
        "resource_group_id": resource_group.id
    }
    if request.method == 'POST':
        form = ResourceForm(request.POST, **parameters)
        if form.is_valid():
            form.save()
            return redirect("resource_tracker:resource_group_resource_list", resource_group.id)
    else:
        form = ResourceForm(**parameters)
    breadcrumbs = [
        {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
        {'text': resource_group.name,
         'url': reverse('resource_tracker:resource_group_resource_list', args=[resource_group_id])},
        {'text': 'New resource', 'url': ""},
    ]
    context = {'resource_group': resource_group, 'form': form, 'breadcrumbs': breadcrumbs, 'action': 'create'}
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def resource_group_resource_edit(request, resource_group_id, resource_id):
    pass


@user_passes_test(lambda u: u.is_superuser)
def resource_group_resource_delete(request, resource_group_id, resource_id):
    pass
