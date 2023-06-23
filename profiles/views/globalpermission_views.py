from django.views.generic import DetailView, UpdateView

from profiles.forms import GlobalPermissionForm
from profiles.models import GlobalPermission

from django.urls import reverse


from profiles.tables import UserRoleTable, ScopeRoleTable


class GlobalPermissionDetailView(DetailView):
    model = GlobalPermission

    def dispatch(self, request, *args, **kwargs):
        self.kwargs['pk'] = GlobalPermission.load().id
        kwargs['pk'] = self.kwargs.get('pk')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Global Permission"
        context['users'] = UserRoleTable(self.object.users)
        context['roles'] = ScopeRoleTable(self.object.roles.all())
        context['scope'] = self.object
        return context


class GlobalPermissionEditView(UpdateView):
    model = GlobalPermission
    template_name = 'generics/generic_form.html'
    form_class = GlobalPermissionForm

    def dispatch(self, request, *args, **kwargs):
        self.kwargs['pk'] = GlobalPermission.load().id
        kwargs['pk'] = self.kwargs.get('pk')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        breadcrumbs = [
            {'text': 'Global permission', 'url': reverse('profiles:globalpermission_details')},
            {'text': f'Roles', 'url': ""},
        ]
        context['breadcrumbs'] = breadcrumbs
        context['action'] = "edit"
        return context
