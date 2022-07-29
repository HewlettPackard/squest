from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe

from service_catalog.forms import PortfolioForm
from service_catalog.models import Service
from service_catalog.models.portfolio import Portfolio


@user_passes_test(lambda u: u.is_superuser)
def portfolio_create(request):
    if request.method == 'POST':
        form = PortfolioForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
            return redirect("service_catalog:portfolio_list")
    else:
        form = PortfolioForm()
    breadcrumbs = [{'text': 'Service catalog', 'url': reverse('service_catalog:service_catalog_list')},
                   {'text': 'Portfolios', 'url': reverse('service_catalog:portfolio_list')},
                   {'text': "Create a portfolio'", 'url': ''}]
    context = {
        'form': form,
        'breadcrumbs': breadcrumbs,
        'action': 'create',
        'multipart': True
    }
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def portfolio_edit(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)
    form = PortfolioForm(request.POST or None, request.FILES or None, instance=portfolio)
    if form.is_valid():
        form.save()
        return redirect("service_catalog:portfolio_list")
    breadcrumbs = [{'text': 'Service catalog', 'url': reverse('service_catalog:service_catalog_list')},
                   {'text': 'Portfolios', 'url': reverse('service_catalog:portfolio_list')},
                   {'text': portfolio.name, 'url': ''}]
    context = {
        'form': form,
        'portfolio': portfolio,
        'breadcrumbs': breadcrumbs,
        'action': 'edit',
        'multipart': True
    }
    return render(request, 'generics/generic_form.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def portfolio_delete(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)
    if request.method == "POST":
        portfolio.delete()
        return redirect("service_catalog:portfolio_list")
    breadcrumbs = [{'text': 'Service catalog', 'url': reverse('service_catalog:service_catalog_list')},
                   {'text': 'Portfolios', 'url': reverse('service_catalog:portfolio_list')},
                   {'text': portfolio.name, 'url': ''}]
    context = {
        'breadcrumbs': breadcrumbs,
        'confirm_text': mark_safe(f"Confirm deletion of <strong>{portfolio}</strong>?"),
        'action_url': reverse('service_catalog:portfolio_delete',
                              kwargs={
                                  'portfolio_id': portfolio_id
                              }),
        'button_text': 'Delete',
        'details': None
    }
    return render(request, "generics/confirm-delete-template.html", context)


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
