from django.core.exceptions import ImproperlyConfigured
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_tables2 import RequestConfig

from Squest.utils.squest_views import *
from profiles.filters.quota import QuotaFilter
from profiles.forms.quota_forms import QuotaForm
from profiles.models import Scope, Quota, Team
from profiles.tables.instance_consumption_table import InstanceConsumptionTable
from profiles.tables.quota_table import QuotaTable
from profiles.tables.team_quota_limit_table import TeamQuotaLimitTable
from resource_tracker_v2.models import ResourceAttribute


def get_breadcrumbs_for_scope(scope):
    class_name = scope.__class__.__name__
    breadcrumbs = [
        {'text': class_name, 'url': reverse(f'profiles:{class_name.lower()}_list')},
        {'text': scope.name, 'url': scope.get_absolute_url() + '#quotas'},
        {'text': 'Quotas', 'url': ''},

    ]
    if isinstance(scope, Team):
        breadcrumbs = [
                          {'text': "Organization", 'url': reverse(f'profiles:organization_list')},
                          {'text': scope.org, 'url': scope.org.get_absolute_url() + '#quotas'},
                      ] + breadcrumbs
    return breadcrumbs


class QuotaListView(SquestListView):
    model = Quota
    filterset_class = QuotaFilter
    table_class = QuotaTable
    ordering = 'attribute_definition__name'
    no_data_message = 'To create quota, go to organization/team and click on "Set quotas"'
    export_csv = True

    def get_context_data(self, **kwargs):
        context = super(QuotaListView, self).get_context_data(**kwargs)
        context['html_button_path'] = ""
        return context


class QuotaEditView(SquestFormView):
    model = Scope
    form_class = QuotaForm
    pk_url_kwarg = "scope_id"

    def get_permission_required(self):
        object = self.get_object()
        if object.is_team:
            return "profiles.change_team_quota"
        elif object.is_org:
            return f"profiles.change_organization_quota"
        else:
            raise ImproperlyConfigured(
                '{0} is missing the permission_required attribute. Define {0}.permission_required, or override '
                '{0}.get_permission_required().'.format(self.__class__.__name__)
            )

    def get_success_url(self):
        return self.scope.get_absolute_url() + "#quotas"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        scope_id = self.kwargs['scope_id']
        self.scope = get_object_or_404(Scope, pk=scope_id)
        kwargs.update({'scope': self.scope})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        breadcrumbs = get_breadcrumbs_for_scope(self.scope.get_object())
        context['breadcrumbs'] = breadcrumbs
        context['action'] = "edit"
        return context


class QuotaDetailsView(SquestDetailView):
    model = Quota

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = RequestConfig(self.request)

        scope = self.object.scope.get_object()
        class_name = scope.__class__.__name__
        context["breadcrumbs"] = [
            {'text': class_name, 'url': reverse_lazy(f"profiles:{class_name.lower()}_list")},
            {'text': f"{self.object.scope.name}", 'url': self.object.scope.get_absolute_url() + "#quotas"},
            {'text': f"Quota", 'url': ''},
            {'text': f"{self.object.name}", 'url': ''},
        ]
        if class_name == "Organization":
            quotas_teams = Quota.objects.filter(scope__in=scope.teams.all(),
                                                attribute_definition=self.object.attribute_definition)
            quotas_teams_consumption = quotas_teams.aggregate(consumed=Sum('limit')).get("consumed", 0)
            context['quotas_teams_consumption'] = quotas_teams_consumption
            context['team_limit_table'] = TeamQuotaLimitTable(quotas_teams.all(), prefix="team-")
            config.configure(context['team_limit_table'])

        resources = ResourceAttribute.objects.filter(attribute_definition=self.object.attribute_definition,
                                                     resource__service_catalog_instance__quota_scope=self.object.scope)
        context['instance_consumption_table'] = InstanceConsumptionTable(resources.all(), prefix="instance-")
        config.configure(context['instance_consumption_table'])
        instances_consumption = resources.all().aggregate(consumed=Sum("value")).get("consumed", 0)
        context['instances_consumption'] = instances_consumption
        return context


class QuotaDeleteView(SquestDeleteView):
    model = Quota
