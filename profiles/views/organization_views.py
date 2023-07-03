from django.db.models import ProtectedError
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView

from Squest.utils.squest_views import SquestListView
from profiles.filters import OrganizationFilter
from profiles.forms import OrganizationForm
from profiles.models import Organization
from profiles.tables import OrganizationTable, UserRoleTable, ScopeRoleTable, TeamTable

from django.urls import reverse
from guardian.mixins import LoginRequiredMixin

from profiles.filters.user_filter import UserFilter
from profiles.tables.quota_table import QuotaTable


class OrganizationListView(SquestListView):
    table_pagination = {'per_page': 10}
    table_class = OrganizationTable
    model = Organization
    template_name = 'generics/list.html'
    ordering = 'name'

    filterset_class = OrganizationFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['html_button_path'] = "generics/buttons/generic_add_button.html"
        return context


class OrganizationDetailView(LoginRequiredMixin, DetailView):
    model = Organization
    filterset_class = UserFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Breadcrumbs
        breadcrumbs = [
            {'text': 'Organizations', 'url': reverse('profiles:organization_list')},
            {'text': f'{self.object}', 'url': ""},
        ]
        context['breadcrumbs'] = breadcrumbs
        context['scope'] = self.object
        context['parent_id'] = self.object.id  # used by generic_actions_with_parent in the table
        context['users'] = UserRoleTable(self.object.users)
        context['teams'] = TeamTable(self.object.teams.all())
        context['roles'] = ScopeRoleTable(self.object.roles.all())
        context['quotas'] = QuotaTable(self.object.quotas.all())
        return context


class OrganizationCreateView(LoginRequiredMixin, CreateView):
    model = Organization
    template_name = 'generics/generic_form.html'
    form_class = OrganizationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        breadcrumbs = [
            {'text': 'Organizations', 'url': reverse('profiles:organization_list')},
            {'text': f'Create organization', 'url': ""},
        ]
        context['breadcrumbs'] = breadcrumbs

        context['action'] = "create"
        return context


class OrganizationEditView(UpdateView):
    model = Organization
    template_name = 'generics/generic_form.html'
    form_class = OrganizationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        breadcrumbs = [
            {'text': 'Organizations', 'url': reverse('profiles:organization_list')},
            {'text': f'{self.object}', 'url': ""},
        ]
        context['breadcrumbs'] = breadcrumbs

        context['action'] = "edit"
        return context


class OrganizationDeleteView(DeleteView):
    model = Organization
    template_name = 'generics/delete.html'
    success_url = reverse_lazy("profiles:organization_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        breadcrumbs = [
            {'text': 'Organizations', 'url': reverse('profiles:organization_list')},
            {'text': f'{self.object}', 'url': ""},
        ]
        context['breadcrumbs'] = breadcrumbs

        return context

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            error_message = f"{e.args[0]}"

            context = self.get_context_data(object=self.object, error_message=error_message,
                                            protected_objects=e.protected_objects)
            return self.render_to_response(context)
