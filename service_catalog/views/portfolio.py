from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe

from Squest.utils.squest_views import *
from service_catalog.filters.portfolio_filter import PortfolioFilter
from service_catalog.forms import PortfolioForm
from service_catalog.models import Service
from service_catalog.models.portfolio import Portfolio
from service_catalog.tables.portfolio_tables import PortfolioTable


class PortfolioListView(SquestListView):
    model = Portfolio
    filterset_class = PortfolioFilter
    table_class = PortfolioTable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Service catalog', 'url': reverse('service_catalog:service_catalog_list')},
            {'text': 'Portfolio', 'url': ''}
        ]
        return context

class PortfolioCreateView(SquestCreateView):
    model = Portfolio
    form_class = PortfolioForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['multipart'] = True
        context['breadcrumbs'] = [
            {'text': 'Service catalog', 'url': reverse('service_catalog:service_catalog_list')},
        ] + context['breadcrumbs']
        return context


class PortfolioEditView(SquestUpdateView):
    model = Portfolio
    form_class = PortfolioForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['multipart'] = True
        context['breadcrumbs'] = [
            {'text': 'Service catalog', 'url': reverse('service_catalog:service_catalog_list')},
        ] + context['breadcrumbs']
        return context


class PortfolioDeleteView(SquestDeleteView):
    model = Portfolio

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Service catalog', 'url': reverse('service_catalog:service_catalog_list')},
        ] + context['breadcrumbs']
        return context


@login_required
def service_catalog_list(request):
    current_portfolio_id = request.GET.get('parent_portfolio') if request.GET.get('parent_portfolio') else None
    current_portfolio = get_object_or_404(Portfolio.objects.all(), id=current_portfolio_id) if current_portfolio_id else None
    sub_portfolio_list = Portfolio.objects.filter(parent_portfolio__id=current_portfolio_id)
    service_list = Service.objects.filter(parent_portfolio__id=current_portfolio_id, enabled=True)
    context = {
        'breadcrumbs': get_portfolio_breadcrumbs(current_portfolio_id),
        'portfolio_list': sub_portfolio_list,
        'service_list': service_list,
        'current_portfolio': current_portfolio
    }
    context['breadcrumbs'][-1]['url'] = ''
    return render(request, "service_catalog/common/service-catalog.html", context)


def get_portfolio_breadcrumbs(parent_portfolio):
    parent_list = Portfolio.objects.get(id=parent_portfolio).get_parents() if parent_portfolio else list()
    breadcrumbs = [{'text': 'Service catalog', 'url': reverse('service_catalog:service_catalog_list')}]
    breadcrumbs += [{'text': parent.name, 'url': get_portfolio_list_url(parent.id)} for parent in parent_list]
    return breadcrumbs


def get_portfolio_list_url(parent_portfolio):
    if Portfolio.objects.filter(id=parent_portfolio).exists():
        return reverse('service_catalog:service_catalog_list') + f"?parent_portfolio={parent_portfolio}"
    return reverse('service_catalog:service_catalog_list')
