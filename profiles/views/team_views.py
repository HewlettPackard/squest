from django.db.models import ProtectedError
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from guardian.mixins import LoginRequiredMixin

from Squest.utils.squest_views import SquestListView
from profiles.filters.team_filter import TeamFilter
from profiles.forms.team_forms import TeamForm
from profiles.models.team import Team
from profiles.models.organization import Organization
from profiles.tables import UserRoleTable, ScopeRoleTable, TeamTable


class TeamListView(SquestListView):
    table_pagination = {'per_page': 10}
    table_class = TeamTable
    model = Team
    template_name = 'generics/list.html'
    ordering = 'name'

    filterset_class = TeamFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['html_button_path'] = "generics/buttons/generic_add_button.html"
        return context


class TeamDetailView(DetailView):
    model = Team

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Breadcrumbs
        breadcrumbs = [
            {'text': 'Teams', 'url': reverse('profiles:team_list')},
            {'text': f'{self.object}', 'url': ""},
        ]
        context['breadcrumbs'] = breadcrumbs
        context['users'] = UserRoleTable(self.object.users)
        context['roles'] = ScopeRoleTable(self.object.roles.all())
        context['scope'] = self.object

        return context


class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    template_name = 'generics/generic_form.html'
    form_class = TeamForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        breadcrumbs = [
            {'text': 'Teams', 'url': reverse('profiles:team_list')},
            {'text': f'Create Team', 'url': ""},
        ]
        context['breadcrumbs'] = breadcrumbs

        context['action'] = "create"
        return context


class OrganizationTeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    template_name = 'generics/generic_form.html'
    form_class = TeamForm

    def get_form_kwargs(self):
        kwargs = super(OrganizationTeamCreateView, self).get_form_kwargs()
        kwargs['organization_id'] = self.kwargs.get('pk')
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        breadcrumbs = [
            {'text': 'Organizations', 'url': reverse('profiles:organization_list')},
            {'text': f'{Organization.objects.get(id=self.kwargs.get("pk"))}',
             'url': reverse('profiles:organization_details', kwargs={"pk": self.kwargs.get("pk")})},
            {'text': f'Create team', 'url': ""},
        ]
        context['breadcrumbs'] = breadcrumbs

        context['action'] = "create"
        return context


class TeamEditView(UpdateView):
    model = Team
    template_name = 'generics/generic_form.html'
    form_class = TeamForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        breadcrumbs = [
            {'text': 'Teams', 'url': reverse('profiles:team_list')},
            {'text': f'{self.object}', 'url': ""},
        ]
        context['breadcrumbs'] = breadcrumbs

        context['action'] = "edit"
        return context


class TeamDeleteView(DeleteView):
    model = Team
    template_name = 'generics/delete.html'
    success_url = reverse_lazy("profiles:team_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        breadcrumbs = [
            {'text': 'Teams', 'url': reverse('profiles:team_list')},
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
