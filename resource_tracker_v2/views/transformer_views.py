from django.shortcuts import render, get_object_or_404

from Squest.utils.squest_views import *
from resource_tracker_v2.filters.transformer_filter import TransformerFilter
from resource_tracker_v2.forms.transformer_form import TransformerForm
from resource_tracker_v2.models import Transformer, ResourceGroup, AttributeDefinition, ResourceAttribute
from resource_tracker_v2.tables.transformer_table import TransformerTable


class TransformerListView(SquestListView):
    model = Transformer
    filterset_class = TransformerFilter
    table_class = TransformerTable

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super(TransformerListView, self).get_filterset_kwargs(filterset_class)
        resource_group = get_object_or_404(ResourceGroup, pk=self.kwargs['resource_group_id'])
        kwargs.update({"resource_group": resource_group})
        return kwargs

    def get_queryset(self):
        return super().get_queryset().filter(resource_group__id=self.kwargs.get('resource_group_id'))

    def get_generic_url(self, action):
        url = super().get_generic_url(action)
        if action == 'create':
            url = reverse_lazy('resource_tracker_v2:transformer_create',
                               kwargs={'resource_group_id': self.kwargs.get('resource_group_id')})
        return url

    def get_context_data(self, **kwargs):
        resource_group = ResourceGroup.objects.get(id=self.kwargs.get('resource_group_id'))
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Resource group', 'url': resource_group.get_absolute_url()},
            {'text': resource_group, 'url': ""},
        ]
        return context


class TransformerCreateView(SquestCreateView):
    model = Transformer
    form_class = TransformerForm
    template_name = 'resource_tracking_v2/resource_group/resource-group-attribute-link.html'

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        resource_group = get_object_or_404(ResourceGroup, pk=self.kwargs['resource_group_id'])
        kwargs.update({'source_resource_group': resource_group})
        return kwargs

    def get_context_data(self, **kwargs):
        resource_group = get_object_or_404(ResourceGroup, pk=self.kwargs['resource_group_id'])
        context = super().get_context_data(**kwargs)
        context["resource_group"] = resource_group
        context['breadcrumbs'] = [
            {'text': "Resource group", 'url': resource_group.get_absolute_url()},
            {'text': resource_group, 'url': reverse('resource_tracker_v2:transformer_list',
                                                    kwargs={"resource_group_id": resource_group.id})},
            {'text': 'Add attribute', 'url': ""}
        ]
        return context


class TransformerEditView(SquestUpdateView):
    model = Transformer
    form_class = TransformerForm
    template_name = 'resource_tracking_v2/resource_group/resource-group-attribute-link-edit.html'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Transformer,
            resource_group_id=self.kwargs['resource_group_id'],
            attribute_definition_id=self.kwargs['attribute_id']
        )

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        resource_group = get_object_or_404(ResourceGroup, pk=self.kwargs['resource_group_id'])
        kwargs.update({'source_resource_group': resource_group})
        return kwargs

    def get_context_data(self, **kwargs):
        resource_group = get_object_or_404(ResourceGroup, pk=self.kwargs['resource_group_id'])
        attribute = get_object_or_404(AttributeDefinition, pk=self.kwargs['attribute_id'])
        context = super().get_context_data(**kwargs)
        context["resource_group"] = resource_group
        context["attribute"] = attribute
        context['breadcrumbs'] = [
            {'text': "Resource group", 'url': resource_group.get_absolute_url()},
            {'text': resource_group, 'url': self.get_object().get_absolute_url()},
            {'text': attribute, 'url': ""}
        ]
        return context


class TransformerDeleteView(SquestDeleteView):
    model = Transformer
    template_name = 'resource_tracking_v2/resource_group/resource-group-attribute-delete.html'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Transformer,
            resource_group_id=self.kwargs['resource_group_id'],
            attribute_definition_id=self.kwargs['attribute_id']
        )

    def get_success_url(self):
        resource_group_id = self.kwargs.get('resource_group_id')
        return reverse("resource_tracker_v2:transformer_list",
                       kwargs={"resource_group_id": resource_group_id})

    def get_context_data(self, **kwargs):
        resource_group = get_object_or_404(ResourceGroup, pk=self.kwargs['resource_group_id'])
        attribute = get_object_or_404(AttributeDefinition, pk=self.kwargs['attribute_id'])
        transformer = Transformer.objects.get(resource_group=resource_group, attribute_definition=attribute)
        impacted_resources = resource_group.resources.filter(
            resource_attribute__in=[attribute for attribute
                                    in ResourceAttribute.objects.filter(
                    attribute_definition=transformer.attribute_definition).all()])
        context = super().get_context_data(**kwargs)
        context["resource_group"] = resource_group
        context["attribute"] = attribute
        context["impacted_resources"] = impacted_resources
        context['breadcrumbs'] = [
            {'text': "Resource group", 'url': resource_group.get_absolute_url()},
            {'text': resource_group, 'url': self.get_object().get_absolute_url()},
            {'text': attribute, 'url': ""}
        ]
        return context


def ajax_load_attribute(request):
    if not request.user.has_perm('resource_tracker_v2.list_transformer'):
        raise PermissionDenied
    current_resource_group_id = request.GET.get('current_resource_group_id')
    target_resource_group_id = request.GET.get('target_resource_group_id')
    current_resource_group = ResourceGroup.objects.get(id=current_resource_group_id)
    target_resource_group = ResourceGroup.objects.get(id=target_resource_group_id)
    all_available_attribute_to_target_rg = Transformer.objects \
        .filter(resource_group=target_resource_group) \
        .exclude(resource_group=current_resource_group, consume_from_resource_group=target_resource_group)

    options = [(transformer.attribute_definition.id, transformer.attribute_definition.name) for transformer in
               all_available_attribute_to_target_rg.all()]
    return render(request, 'service_catalog/settings/global_hooks/state-dropdown-list-option.html',
                  {'options': options})
