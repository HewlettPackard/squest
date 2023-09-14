from django.shortcuts import render, get_object_or_404

from Squest.utils.squest_model import SquestDeleteCascadeMixIn
from Squest.utils.squest_views import *
from resource_tracker_v2.filters.transformer_filter import TransformerFilter
from resource_tracker_v2.forms.transformer_form import TransformerForm
from resource_tracker_v2.models import Transformer, ResourceGroup, AttributeDefinition, Resource
from resource_tracker_v2.tables.transformer_table import TransformerTable


class TransformerListView(SquestListView):
    model = Transformer
    filterset_class = TransformerFilter
    table_class = TransformerTable

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
    template_name = 'resource_tracker_v2/resource_group/resource-group-attribute-link.html'

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
    template_name = 'resource_tracker_v2/resource_group/resource-group-attribute-link-edit.html'

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
        context = super().get_context_data(**kwargs)
        context["resource_group"] = resource_group
        context["attribute"] = attribute
        resource_impacted = [SquestDeleteCascadeMixIn.format_callback(squest_object) for squest_object in
            Resource.objects.filter(
                resource_group=self.get_object().resource_group,
                resource_attribute__attribute_definition=self.get_object().attribute_definition
            )
        ]
        context['details'] = {
            'warning_sentence': 'Related will be impacted:',
            'details_list': self.object.get_related_objects_cascade() + resource_impacted
        }
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
    if target_resource_group_id != "":
        target_resource_group = ResourceGroup.objects.get(id=target_resource_group_id)
        options = Transformer.objects.filter(resource_group=target_resource_group)\
            .exclude(resource_group=current_resource_group,
                     consume_from_resource_group=target_resource_group).values_list('attribute_definition__id', 'attribute_definition__name')
    else:
        # remove consume from on attribute from the transformer
        options = ["---------", "---------"]

    return render(request, 'generics/ajax-option.html',
                  {'options': options})
