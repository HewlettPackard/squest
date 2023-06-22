from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from Squest.utils.squest_views import SquestListView
from resource_tracker_v2.filters.attribute_definition_filter import AttributeDefinitionFilter
from resource_tracker_v2.forms.attribute_definition_form import AttributeDefinitionForm
from resource_tracker_v2.models import AttributeDefinition, ResourceGroup, Transformer
from resource_tracker_v2.tables.attribute_defintion_table import AttributeDefinitionTable


class AttributeDefinitionListView(SquestListView):
    permission_required = "is_superuser"
    table_class = AttributeDefinitionTable
    model = AttributeDefinition
    filterset_class = AttributeDefinitionFilter
    template_name = 'generics/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['html_button_path'] = "generics/buttons/generic_add_button.html"
        return context


class AttributeDefinitionCreateView(PermissionRequiredMixin, CreateView):
    model = AttributeDefinition
    template_name = 'generics/generic_form.html'
    form_class = AttributeDefinitionForm
    permission_required = "is_superuser"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Attribute definition"
        context['app_name'] = "resource_tracker_v2"
        context['object_name'] = "attribute_definition"
        context['action'] = "create"
        context[""] = [
            {'text': 'Attribute definition', 'url': reverse('resource_tracker_v2:attributedefinition_list')},
            {'text': 'Create a new attribute definition', 'url': ""},
        ]
        return context


class AttributeDefinitionEditView(PermissionRequiredMixin, UpdateView):
    model = AttributeDefinition
    template_name = 'generics/generic_form.html'
    form_class = AttributeDefinitionForm
    permission_required = "is_superuser"
    pk_url_kwarg = "attribute_definition_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        content_type = ContentType.objects.get_for_model(self.model)

        context['title'] = f'Edit {content_type.name}'
        context['app_name'] = content_type.app_label
        context['object_name'] = content_type.model
        context['action'] = "edit"
        context[""] = [
            {'text': 'Attribute definition', 'url': reverse('resource_tracker_v2:attributedefinition_list')},
            {'text': self.object.name, 'url': ""},
        ]
        return context


class AttributeDefinitionDeleteView(PermissionRequiredMixin, DeleteView):
    model = AttributeDefinition
    template_name = 'resource_tracking_v2/attributes/attribute-definition-delete.html'
    success_url = reverse_lazy("resource_tracker_v2:attributedefinition_list")
    permission_required = "is_superuser"
    pk_url_kwarg = "attribute_definition_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        impacted_resource_group = ResourceGroup.objects.filter(id__in=Transformer.objects.filter(attribute_definition=kwargs.get("object")).values_list("resource_group__id", flat=True))
        context['impacted_resource_group'] = impacted_resource_group
        breadcrumbs = [
            {'text': 'Attribute definition', 'url': reverse('resource_tracker_v2:attributedefinition_list')},
            {'text': self.object.name, 'url': ""},
        ]
        context['breadcrumbs'] = breadcrumbs
        return context
