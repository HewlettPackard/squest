from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from guardian.mixins import LoginRequiredMixin

from service_catalog.filters.custom_link_filter import CustomLinkFilter
from service_catalog.forms.custom_link_form import CustomLinkForm
from service_catalog.models import CustomLink
from service_catalog.tables.custom_link_table import CustomLinkTable


@method_decorator(login_required, name='dispatch')
class CustomLinkListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = CustomLinkTable
    model = CustomLink
    template_name = 'generics/list.html'
    filterset_class = CustomLinkFilter

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied
        return super(CustomLinkListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Custom links"
        context['app_name'] = "service_catalog"
        context['object_name'] = "custom_link"
        context['html_button_path'] = "generics/buttons/generic_add_button.html"
        return context


@user_passes_test(lambda u: u.is_superuser)
def custom_link_create(request):
    if request.method == 'POST':
        form = CustomLinkForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('service_catalog:custom_link_list')
    else:
        form = CustomLinkForm()
    breadcrumbs = [
        {'text': 'Custom link', 'url': reverse('service_catalog:custom_link_list')},
        {'text': "Create a new custom_link", 'url': ""}
    ]
    context = {'form': form, 'breadcrumbs': breadcrumbs, 'action': 'create'}
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def custom_link_edit(request, custom_link_id):
    custom_link = get_object_or_404(CustomLink, id=custom_link_id)
    form = CustomLinkForm(request.POST or None, instance=custom_link)
    if form.is_valid():
        form.save()
        return redirect('service_catalog:custom_link_list')
    breadcrumbs = [
        {'text': 'Custom link', 'url': reverse('service_catalog:custom_link_list')},
        {'text': custom_link.name, 'url': ""}
    ]
    context = {'form': form,
               'custom_link': custom_link,
               'breadcrumbs': breadcrumbs,
               'action': 'edit'
               }
    return render(request, 'generics/generic_form.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def custom_link_delete(request, custom_link_id):
    custom_link = get_object_or_404(CustomLink, id=custom_link_id)
    if request.method == "POST":
        custom_link.delete()
        return redirect('service_catalog:custom_link_list')
    breadcrumbs = [
        {'text': 'Custom link', 'url': reverse('service_catalog:custom_link_list')},
        {'text': custom_link.name, 'url': ""}
    ]
    context = {
        'breadcrumbs': breadcrumbs,
        'confirm_text': mark_safe(f"Confirm deletion of <strong>{custom_link.name}</strong>?"),
        'action_url': reverse('service_catalog:custom_link_delete', args=[custom_link_id]),
        'button_text': 'Delete',
    }
    return render(request, "generics/confirm-delete-template.html", context)
