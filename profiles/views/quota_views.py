from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import FormView, DetailView

from profiles.forms.quota_forms import QuotaForm
from profiles.models import Scope, Quota
from profiles.tables.instance_consumption_table import InstanceConsumptionTable
from profiles.tables.team_quota_limit_table import TeamQuotaLimitTable
from resource_tracker_v2.models import ResourceAttribute


class QuotaEditView(FormView):
    template_name = 'generics/generic_form.html'
    form_class = QuotaForm
    pk_url_kwarg = "scope_id"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

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
        class_name = self.scope.get_object().__class__.__name__
        breadcrumbs = [
            {'text': class_name, 'url': reverse(f"profiles:{class_name.lower()}_list")},
            {'text': f"{self.scope.name}",
             'url': self.scope.get_absolute_url() + "#quotas"},
            {'text': f'Quotas', 'url': ""},
        ]
        context['breadcrumbs'] = breadcrumbs
        context['action'] = "edit"
        return context


class QuotaDetailsView(DetailView):
    model = Quota
    template_name = 'profiles/quota_detail.html'
    pk_url_kwarg = "quota_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scope = self.object.scope.get_object()
        class_name = scope.__class__.__name__
        context["breadcrumbs"] = [
            {'text': class_name, 'url': reverse(f"profiles:{class_name.lower()}_list")},
            {'text': f"{self.object.scope.name}", 'url': self.object.scope.get_absolute_url() + "#quotas"},
            {'text': f"Quota", 'url': ''},
            {'text': f"{self.object.name}", 'url': ''},
        ]
        if class_name == "Organization":
            quotas_teams = Quota.objects.filter(scope__in=scope.teams.all(),
                                                attribute_definition=self.object.attribute_definition)
            quotas_teams_consumption = quotas_teams.aggregate(consumed=Sum('limit')).get("consumed", 0)
            context['quotas_teams_consumption'] = quotas_teams_consumption
            context['team_limit_table'] = TeamQuotaLimitTable(quotas_teams.all())

        resources = ResourceAttribute.objects.filter(attribute_definition=self.object.attribute_definition,
                                                     resource__service_catalog_instance__quota_scope=self.object.scope)
        context['instance_consumption_table'] = InstanceConsumptionTable(resources.all())
        instances_consumption = resources.all().aggregate(consumed=Sum("value")).get("consumed", 0)
        context['instances_consumption'] = instances_consumption
        return context
