from django.urls import reverse

from Squest.utils.squest_views import *
from profiles.forms import GlobalPermissionForm
from profiles.models import GlobalPermission
from profiles.tables import UserRoleTable, PermissionTable


class GlobalPermissionDetailView(SquestDetailView):
    model = GlobalPermission

    def get_object(self, queryset=None):
        return GlobalPermission.load()

    def dispatch(self, request, *args, **kwargs):
        self.kwargs['pk'] = self.get_object().id
        kwargs['pk'] = self.kwargs.get('pk')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = None
        context['users'] = UserRoleTable(self.object.users)
        permission_table = PermissionTable(self.object.user_permissions.all())
        permission_table.exclude = ("actions",)

        context['user_permissions'] = permission_table
        return context


class GlobalPermissionEditView(SquestUpdateView):
    model = GlobalPermission
    form_class = GlobalPermissionForm

    def get_object(self, queryset=None):
        return GlobalPermission.load()

    def get_generic_url(self, action):
        return reverse_lazy('profiles:globalpermission_details')

    def dispatch(self, request, *args, **kwargs):
        self.kwargs['pk'] = self.get_object().id
        kwargs['pk'] = self.kwargs.get('pk')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Global permission', 'url': reverse('profiles:globalpermission_details')},
            {'text': f'Edit', 'url': ""},
        ]
        return context
