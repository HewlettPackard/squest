from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Permission
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from Squest.utils.squest_views import SquestListView
from profiles.filters import PermissionFilter
from profiles.forms.permission_form import PermissionForm
from profiles.tables import PermissionTable


class PermissionListView(SquestListView):
    table_pagination = {'per_page': 10}
    table_class = PermissionTable
    model = Permission
    template_name = 'generics/list.html'
    ordering = 'name'
    filterset_class = PermissionFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app_name'] = "profiles"
        context['html_button_path'] = "generics/buttons/generic_add_button.html"
        return context


class PermissionCreateView(LoginRequiredMixin, CreateView):
    model = Permission
    template_name = 'generics/generic_form.html'
    form_class = PermissionForm
    success_url = reverse_lazy('profiles:permission_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        breadcrumbs = [
            {'text': 'Permissions', 'url': reverse('profiles:permission_list')},
            {'text': f'New permissions', 'url': ""},
        ]
        context['breadcrumbs'] = breadcrumbs
        context['action'] = "create"
        return context


class PermissionEditView(UpdateView):
    model = Permission
    template_name = 'generics/generic_form.html'
    form_class = PermissionForm
    success_url = reverse_lazy('profiles:permission_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        breadcrumbs = [
            {'text': 'Permissions', 'url': reverse('profiles:permission_list')},
            {'text': f'{self.object}', 'url': ""},
        ]
        context['breadcrumbs'] = breadcrumbs
        context['action'] = "edit"
        return context


class PermissionDeleteView(DeleteView):
    model = Permission
    template_name = 'generics/delete.html'
    success_url = reverse_lazy('profiles:permission_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        breadcrumbs = [
            {'text': 'Permissions', 'url': reverse('profiles:permission_list')},
            {'text': f'{self.object}', 'url': ""},
        ]
        context['breadcrumbs'] = breadcrumbs
        return context
