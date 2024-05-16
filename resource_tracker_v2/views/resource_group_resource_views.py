from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from Squest.utils.squest_views import *
from resource_tracker_v2.filters.resource_filter import ResourceFilter
from resource_tracker_v2.forms.resource_form import ResourceForm, ResourceMoveForm
from resource_tracker_v2.models import Resource, ResourceGroup
from resource_tracker_v2.tables.resource_table import ResourceTable
from resource_tracker_v2.views.utils.tag_filter_list_view import TagFilterListView


class ResourceListView(TagFilterListView):
    model = Resource
    filterset_class = ResourceFilter
    table_class = ResourceTable

    def get_queryset(self):
        return super().get_queryset().filter(resource_group_id=self.kwargs.get('resource_group_id'))

    def get_context_data(self, **kwargs):
        resource_group = get_object_or_404(ResourceGroup, id=self.kwargs.get('resource_group_id'))
        context = super().get_context_data(**kwargs)
        context['resource_group_id'] = resource_group.id
        context['breadcrumbs'] = [
            {'text': 'Resource group', 'url': reverse('resource_tracker_v2:resourcegroup_list')},
            {'text': resource_group, 'url': ""},
            {'text': "Resource", 'url': ""}
        ]
        context['action_url'] = reverse(
            'resource_tracker_v2:resource_bulk_delete', kwargs={
                "resource_group_id": resource_group.id
            }
        )
        context['html_button_path'] = "resource_tracker_v2/resource_group/resources/resource_list_buttons.html"
        return context


class ResourceCreateView(SquestCreateView):
    form_class = ResourceForm
    model = Resource

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        self.resource_group = get_object_or_404(ResourceGroup, pk=self.kwargs['resource_group_id'])
        kwargs.update({'resource_group': self.resource_group})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["resource_group"] = self.resource_group
        context['breadcrumbs'] = [
            {'text': 'Resource group', 'url': reverse('resource_tracker_v2:resourcegroup_list')},
            {'text': self.resource_group,
             'url': reverse('resource_tracker_v2:resource_list', args=[self.resource_group.id])},
            {'text': 'New resource', 'url': ""},
        ]
        return context


class ResourceEditView(SquestUpdateView):
    model = Resource
    form_class = ResourceForm
    template_name = 'generics/generic_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        resource_group_id = self.kwargs['resource_group_id']
        resource_group = get_object_or_404(ResourceGroup, pk=resource_group_id)
        kwargs.update({'resource_group': resource_group})
        return kwargs

    def get_context_data(self, **kwargs):
        resource_group = ResourceGroup.objects.get(id=self.kwargs.get('resource_group_id'))
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            {'text': 'Resource group', 'url': reverse('resource_tracker_v2:resourcegroup_list')},
            {'text': resource_group,
             'url': reverse('resource_tracker_v2:resource_list', args=[resource_group.id])},
            {'text': self.get_object(), 'url': ""},
        ]
        return context


class ResourceDeleteView(SquestDeleteView):
    model = Resource

    def get_generic_url_kwargs(self):
        return {"resource_group_id": self.kwargs.get('resource_group_id')}


class ResourceMoveView(SquestUpdateView):
    model = Resource
    form_class = ResourceMoveForm

    def get_context_data(self, **kwargs):
        resource_group = get_object_or_404(ResourceGroup, id=self.kwargs.get('resource_group_id'))
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            {'text': 'Resource group', 'url': reverse('resource_tracker_v2:resourcegroup_list')},
            {'text': resource_group,
             'url': reverse('resource_tracker_v2:resource_list', args=[resource_group.id])},
            {'text': self.get_object(), 'url': ""},
            {'text': "Move", 'url': ""},
        ]
        return context


def resource_group_resource_bulk_delete(request, resource_group_id):
    context = dict()
    context['breadcrumbs'] = [
        {'text': 'Resource group', 'url': reverse('resource_tracker_v2:resourcegroup_list')},
        {'text': 'Resources', 'url': reverse('resource_tracker_v2:resource_list',
                                             kwargs={'resource_group_id': resource_group_id})},
        {'text': "Delete multiple", 'url': ""}
    ]
    context['confirm_text'] = mark_safe(f"Confirm deletion of the following resources?")
    context['action_url'] = reverse(
        'resource_tracker_v2:resource_bulk_delete', kwargs={
            "resource_group_id": resource_group_id
        }
    )
    context['button_text'] = 'Delete'
    if request.method == "GET":
        pks = request.GET.getlist("selection")
    if request.method == "POST":
        pks = request.POST.getlist("selection")

    context["object_list"] = Resource.get_queryset_for_user(request.user, 'resource_tracker_v2.delete_resource',
                                                            unique=False).filter(pk__in=pks)
    if context['object_list'].count() != len(pks):
        raise PermissionDenied

    if not context['object_list']:
        messages.warning(request, 'Empty selection.')
        return redirect('resource_tracker_v2:resource_list', resource_group_id=resource_group_id)

    if request.method == "GET":
        return render(request, 'generics/confirm-bulk-delete-template.html', context=context)

    elif request.method == "POST":
        for resource in context['object_list']:  # loop to transform the queryset into objects
            resource.delete()
        return redirect("resource_tracker_v2:resource_list", resource_group_id)
