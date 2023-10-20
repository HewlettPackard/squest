from Squest.utils.squest_table import SquestRequestConfig

from Squest.utils.squest_views import *
from profiles.tables.quota_table import QuotaTable
from resource_tracker_v2.filters.attribute_definition_filter import AttributeDefinitionFilter
from resource_tracker_v2.forms.attribute_definition_form import AttributeDefinitionForm
from resource_tracker_v2.models import AttributeDefinition, ResourceGroup, Transformer
from resource_tracker_v2.tables.attribute_defintion_table import AttributeDefinitionTable


class AttributeDefinitionDetailView(SquestDetailView):
    model = AttributeDefinition
    template_name = "resource_tracker_v2/attributedefinition_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = SquestRequestConfig(self.request)
        if self.request.user.has_perm("profiles.view_quota", self.get_object()):
            context['quotas'] = QuotaTable\
                (self.object.quotas.distinct(),
                hide_fields=["attribute_definition"],
                 prefix="quota-"
            )
            config.configure(context['quotas'])

        context['breadcrumbs'] = [
            {
                'text': self.django_content_type.name.capitalize(),
                'url': self.get_generic_url('list')
            },
            {
                'text': self.get_object().name,
                'url': ""
            },
        ]
        return context


class AttributeDefinitionListView(SquestListView):
    table_class = AttributeDefinitionTable
    model = AttributeDefinition
    filterset_class = AttributeDefinitionFilter


class AttributeDefinitionCreateView(SquestCreateView):
    model = AttributeDefinition
    form_class = AttributeDefinitionForm


class AttributeDefinitionEditView(SquestUpdateView):
    model = AttributeDefinition
    form_class = AttributeDefinitionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'][0]['url'] = reverse_lazy('resource_tracker_v2:attributedefinition_list')
        return context


class AttributeDefinitionDeleteView(SquestDeleteView):
    model = AttributeDefinition

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        impacted_resource_group = ResourceGroup.objects.filter(
            id__in=Transformer.objects.filter(
                attribute_definition=kwargs.get("object"))
            .values_list("resource_group__id", flat=True))
        context['breadcrumbs'][0]['url'] = reverse_lazy('resource_tracker_v2:attributedefinition_list')
        return context
