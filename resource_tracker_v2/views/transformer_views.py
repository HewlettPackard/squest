from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from resource_tracker_v2.filters.transformer_filter import TransformerFilter
from resource_tracker_v2.forms.transformer_form import TransformerForm
from resource_tracker_v2.models import Transformer, ResourceGroup, AttributeDefinition, ResourceAttribute
from resource_tracker_v2.tables.transformer_table import TransformerTable


class TransformerListView(PermissionRequiredMixin, SingleTableMixin, FilterView):
    permission_required = "is_superuser"
    table_class = TransformerTable
    model = Transformer
    filterset_class = TransformerFilter
    template_name = 'generics/list.html'

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super(TransformerListView, self).get_filterset_kwargs(filterset_class)
        resource_group_id = self.kwargs.get('resource_group_id')
        resource_group = ResourceGroup.objects.get(id=resource_group_id)
        kwargs.update({"resource_group": resource_group})
        return kwargs

    def get_table_data(self, **kwargs):
        filtered = super().get_table_data().distinct()
        resource_group_id = self.kwargs.get('resource_group_id')
        resource_group = ResourceGroup.objects.get(id=resource_group_id)
        # get all transformer of this resource group
        transformers = Transformer.objects.filter(resource_group__id__in=[resource_group.id]).distinct() & filtered
        return transformers

    def get_context_data(self, **kwargs):
        resource_group_id = self.kwargs.get('resource_group_id')
        resource_group = ResourceGroup.objects.get(id=resource_group_id)
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
            {'text': resource_group.name, 'url': ""},
        ]
        context['title'] = "Resource group attribute"
        context['app_name'] = "resource_tracker"
        context['object_name'] = "transformer"
        context['resource_group_id'] = resource_group_id
        context['html_button_path'] = "resource_tracking_v2/resource_group/resource_group_attribute_list_buttons.html"
        return context


class TransformerCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "is_superuser"
    model = Transformer
    form_class = TransformerForm
    template_name = 'resource_tracking_v2/resource_group/resource-group-attribute-link.html'

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        resource_group_id = self.kwargs['resource_group_id']
        resource_group = get_object_or_404(ResourceGroup, pk=resource_group_id)
        kwargs.update({'source_resource_group': resource_group})
        return kwargs

    def get_context_data(self, **kwargs):
        resource_group_id = self.kwargs.get('resource_group_id')
        resource_group = ResourceGroup.objects.get(id=resource_group_id)
        context = super().get_context_data(**kwargs)
        context["resource_group"] = resource_group
        context['breadcrumbs'] = [
            {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
            {'text': resource_group.name, 'url': reverse('resource_tracker:resource_group_attribute_list',
                                                         kwargs={"resource_group_id": resource_group_id})},
            {'text': "Add attribute", 'url': ""},
        ]
        return context


class TransformerEditView(PermissionRequiredMixin, UpdateView):
    permission_required = "is_superuser"
    model = Transformer
    form_class = TransformerForm
    template_name = 'resource_tracking_v2/resource_group/resource-group-attribute-link-edit.html'

    def get_object(self, queryset=None):
        resource_group_id = self.kwargs['resource_group_id']
        attribute_definition_id = self.kwargs['attribute_id']
        return Transformer.objects.get(resource_group_id=resource_group_id, attribute_definition_id=attribute_definition_id)

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        resource_group_id = self.kwargs['resource_group_id']
        resource_group = get_object_or_404(ResourceGroup, pk=resource_group_id)
        kwargs.update({'source_resource_group': resource_group})
        return kwargs

    def get_context_data(self, **kwargs):
        resource_group_id = self.kwargs.get('resource_group_id')
        resource_group = ResourceGroup.objects.get(id=resource_group_id)
        attribute_definition_id = self.kwargs['attribute_id']
        attribute = AttributeDefinition.objects.get(id=attribute_definition_id)
        context = super().get_context_data(**kwargs)
        context["resource_group"] = resource_group
        context["attribute"] = attribute
        context['breadcrumbs'] = [
            {'text': "Resource groups", 'url': reverse('resource_tracker:resource_group_list')},
            {'text': f"{resource_group.name}", 'url': reverse('resource_tracker:resource_group_attribute_list',
                                                              kwargs={
                                                                  'resource_group_id': resource_group.id,
                                                              })},
            {'text': f"{attribute.name}", 'url': ""}
        ]
        return context


class TransformerDeleteView(PermissionRequiredMixin, DeleteView):
    model = AttributeDefinition
    template_name = 'resource_tracking_v2/resource_group/resource-group-attribute-delete.html'
    permission_required = "is_superuser"

    def get_object(self, queryset=None):
        resource_group_id = self.kwargs['resource_group_id']
        attribute_definition_id = self.kwargs['attribute_id']
        return Transformer.objects.get(resource_group_id=resource_group_id, attribute_definition_id=attribute_definition_id)

    def get_success_url(self):
        resource_group_id = self.kwargs.get('resource_group_id')
        return reverse("resource_tracker:resource_group_attribute_list",
                       kwargs={"resource_group_id": resource_group_id})

    def get_context_data(self, **kwargs):
        resource_group_id = self.kwargs.get('resource_group_id')
        resource_group = ResourceGroup.objects.get(id=resource_group_id)
        attribute_definition_id = self.kwargs['attribute_id']
        attribute_definition = AttributeDefinition.objects.get(id=attribute_definition_id)
        transformer = Transformer.objects.get(resource_group=resource_group, attribute_definition=attribute_definition)
        impacted_resources = resource_group.resources.filter(
            resource_attribute__in=[attribute for attribute
                                    in ResourceAttribute.objects.filter(attribute_definition=transformer.attribute_definition).all()])
        context = super().get_context_data(**kwargs)
        context["resource_group"] = resource_group
        context["attribute"] = attribute_definition
        context["impacted_resources"] = impacted_resources
        context['breadcrumbs'] = [
            {'text': "Resource groups", 'url': reverse('resource_tracker:resource_group_list')},
            {'text': f"{resource_group.name}", 'url': reverse('resource_tracker:resource_group_attribute_list',
                                                              kwargs={
                                                                  'resource_group_id': resource_group.id,
                                                              })},
            {'text': f"{attribute_definition.name}", 'url': ""}
        ]
        return context


@user_passes_test(lambda u: u.is_superuser)
def ajax_load_attribute(request):
    current_resource_group_id = request.GET.get('current_resource_group_id')
    target_resource_group_id = request.GET.get('target_resource_group_id')
    current_resource_group = ResourceGroup.objects.get(id=current_resource_group_id)

    target_resource_group = ResourceGroup.objects.get(id=target_resource_group_id)

    all_available_attribute_to_target_rg = Transformer.objects.filter(resource_group=target_resource_group)

    already_linked = Transformer.objects.filter(resource_group=current_resource_group,
                                                consume_from_resource_group=target_resource_group)
    # exclude already linked
    all_available_attribute_to_target_rg = all_available_attribute_to_target_rg.exclude(id__in=[transformer.consume_from_attribute_definition.id for transformer in already_linked])

    options = [(transformer.attribute_definition.id, transformer.attribute_definition.name) for transformer in all_available_attribute_to_target_rg.all()]
    return render(request, 'service_catalog/settings/global_hooks/state-dropdown-list-option.html',
                  {'options': options})
