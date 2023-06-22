from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, UpdateView, DeleteView

from resource_tracker_v2.filters.resource_filter import ResourceFilter
from resource_tracker_v2.forms.resource_form import ResourceForm
from resource_tracker_v2.models import Resource, ResourceGroup
from resource_tracker_v2.tables.resource_table import ResourceTable
from resource_tracker_v2.views.utils.tag_filter_list_view import TagFilterListView


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
            {'text': 'Resource groups', 'url': reverse('resource_tracker_v2:resourcegroup_list')},
            {'text': resource_group.name, 'url': ""},
            {'text': "Resources", 'url': ""}
        ]
        context['action_url'] = reverse('resource_tracker_v2:resourcegroup_resource_bulk_delete_confirm',
                                        kwargs={'resource_group_id': resource_group_id})
        context['html_button_path'] = "resource_tracking_v2/resource_group/resources/resource_list_buttons.html"
        return context


class ResourceCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "is_superuser"
    form_class = ResourceForm
    model = Resource
    template_name = 'generics/generic_form.html'

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        resource_group_id = self.kwargs['resource_group_id']
        resource_group = get_object_or_404(ResourceGroup, pk=resource_group_id)
        kwargs.update({'resource_group': resource_group})
        return kwargs

    def get_context_data(self, **kwargs):
        resource_group_id = self.kwargs.get('resource_group_id')
        resource_group = ResourceGroup.objects.get(id=resource_group_id)
        context = super().get_context_data(**kwargs)
        context["resource_group"] = resource_group
        context["action"] = "create"
        context['breadcrumbs'] = [
            {'text': 'Resource groups', 'url': reverse('resource_tracker_v2:resourcegroup_list')},
            {'text': resource_group.name,
             'url': reverse('resource_tracker_v2:resourcegroup_resource_list', args=[resource_group_id])},
            {'text': 'New resource', 'url': ""},
        ]
        return context


class ResourceEditView(PermissionRequiredMixin, UpdateView):
    permission_required = "is_superuser"
    model = Resource
    form_class = ResourceForm
    template_name = 'generics/generic_form.html'
    pk_url_kwarg = "resource_id"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        resource_group_id = self.kwargs['resource_group_id']
        resource_group = get_object_or_404(ResourceGroup, pk=resource_group_id)
        kwargs.update({'resource_group': resource_group})
        return kwargs

    def get_context_data(self, **kwargs):
        resource_group_id = self.kwargs.get('resource_group_id')
        resource_group = ResourceGroup.objects.get(id=resource_group_id)
        resource_id = self.kwargs.get('resource_id')
        resource = Resource.objects.get(id=resource_id)
        context = super().get_context_data(**kwargs)

        content_type = ContentType.objects.get_for_model(self.model)

        context['title'] = f'Edit {content_type.name}'
        context['app_name'] = content_type.app_label
        context['object_name'] = content_type.model
        context['action'] = "edit"
        context[""] = [
            {'text': 'Resource groups', 'url': reverse('resource_tracker_v2:resourcegroup_list')},
            {'text': resource_group.name,
             'url': reverse('resource_tracker_v2:resourcegroup_resource_list', args=[resource_group_id])},
            {'text': resource.name, 'url': ""},
        ]
        return context


class ResourceDeleteView(PermissionRequiredMixin, DeleteView):
    model = Resource
    template_name = "resource_tracking_v2/resource_group/resources/resource-delete.html"
    permission_required = "is_superuser"
    pk_url_kwarg = "resource_id"

    def get_success_url(self):
        resource_group_id = self.kwargs.get('resource_group_id')
        return reverse("resource_tracker_v2:resourcegroup_resource_list",
                       kwargs={"resource_group_id": resource_group_id})

    def get_context_data(self, **kwargs):
        resource_group_id = self.kwargs.get('resource_group_id')
        resource_group = ResourceGroup.objects.get(id=resource_group_id)
        resource_id = self.kwargs.get('resource_id')
        resource = Resource.objects.get(id=resource_id)
        context = super().get_context_data(**kwargs)
        context["resource"] = resource
        context["resource_group"] = resource_group
        context['breadcrumbs'] = [
            {'text': 'Resource groups', 'url': reverse('resource_tracker_v2:resourcegroup_list')},
            {'text': resource_group.name,
             'url': reverse('resource_tracker_v2:resourcegroup_resource_list', args=[resource_group_id])},
            {'text': resource.name, 'url': ""},
        ]
        return context


@user_passes_test(lambda u: u.is_superuser)
def resource_group_resource_bulk_delete(request, resource_group_id):
    if request.method == "POST":
        pks = request.POST.getlist("selection")
        selected_resources = Resource.objects.filter(pk__in=pks)
        selected_resources.delete()
    return redirect("resource_tracker_v2:resourcegroup_resource_list", resource_group_id)


@user_passes_test(lambda u: u.is_superuser)
def resource_group_resource_bulk_delete_confirm(request, resource_group_id):
    context = {
        'breadcrumbs': [
            {'text': 'Resource groups', 'url': reverse('resource_tracker_v2:resourcegroup_list')},
            {'text': 'Resources', 'url': reverse('resource_tracker_v2:resourcegroup_resource_list',
                                                 kwargs={'resource_group_id': resource_group_id})},
            {'text': "Delete multiple", 'url': ""}
        ],
        'confirm_text': mark_safe(f"Confirm deletion of the following resources?"),
        'action_url': reverse('resource_tracker_v2:resourcegroup_resource_bulk_delete', kwargs={
            "resource_group_id": resource_group_id
        }),
        'button_text': 'Delete',
    }

    if request.method == "POST":
        pks = request.POST.getlist("selection")
        context['object_list'] = Resource.objects.filter(pk__in=pks)
        if context['object_list']:
            return render(request, 'generics/confirm-bulk-delete-template.html', context=context)
    messages.warning(request, 'No resources selected for deletion.')
    return redirect('resource_tracker_v2:resourcegroup_resource_list', resource_group_id=resource_group_id)
