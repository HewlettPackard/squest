from django.db.models import ProtectedError
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView

from Squest.utils.squest_views import SquestListView
from profiles.filters import RoleFilter
from profiles.forms import RoleForm
from profiles.models import Role
from profiles.tables import RoleTable, PermissionTable

from django.urls import reverse
from guardian.mixins import LoginRequiredMixin

from profiles.filters.user_filter import UserFilter


class RoleListView(SquestListView):
    table_pagination = {'per_page': 10}
    table_class = RoleTable
    model = Role
    template_name = 'generics/list.html'
    ordering = 'name'

    filterset_class = RoleFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['html_button_path'] = "generics/buttons/generic_add_button.html"
        return context


class RoleDetailView(LoginRequiredMixin, DetailView):
    model = Role
    filterset_class = UserFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Breadcrumbs
        breadcrumbs = [
            {'text': 'Roles', 'url': reverse('profiles:role_list')},
            {'text': f'{self.object}', 'url': ""},
        ]
        context['breadcrumbs'] = breadcrumbs
        context['scope'] = self.object

        context['permissions_table'] = PermissionTable(self.object.permissions.all())
        return context


class RoleCreateView(LoginRequiredMixin, CreateView):
    model = Role
    template_name = 'generics/generic_form.html'
    form_class = RoleForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        breadcrumbs = [
            {'text': 'Roles', 'url': reverse('profiles:role_list')},
            {'text': f'Create role', 'url': ""},
        ]
        context['breadcrumbs'] = breadcrumbs

        context['action'] = "create"
        return context


class RoleEditView(UpdateView):
    model = Role
    template_name = 'generics/generic_form.html'
    form_class = RoleForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        breadcrumbs = [
            {'text': 'Roles', 'url': reverse('profiles:role_list')},
            {'text': f'{self.object}', 'url': ""},
        ]
        context['breadcrumbs'] = breadcrumbs

        context['action'] = "edit"
        return context


class RoleDeleteView(DeleteView):
    model = Role
    template_name = 'generics/delete.html'
    success_url = reverse_lazy("profiles:role_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        breadcrumbs = [
            {'text': 'Roles', 'url': reverse('profiles:role_list')},
            {'text': f'{self.object}', 'url': ""},
        ]
        context['breadcrumbs'] = breadcrumbs

        return context

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            error_message = f"{e.args[0]}"
            # Vous pouvez personnaliser le message d'erreur en fonction de vos besoins
            context = self.get_context_data(object=self.object, error_message=error_message,
                                            protected_objects=e.protected_objects)
            return self.render_to_response(context)
