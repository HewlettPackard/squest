from Squest.utils.squest_views import *
from profiles.forms import GlobalScopeForm
from profiles.models import GlobalScope
from profiles.tables import UserRoleTable, PermissionTable


class GlobalScopeRBACView(SquestDetailView):
    model = GlobalScope
    template_name = "profiles/globalscope_rbac_detail.html"

    def get_permission_required(self):
        return "profiles.view_users_globalscope"

    def get_object(self, queryset=None):
        return GlobalScope.load()

    def dispatch(self, request, *args, **kwargs):
        self.kwargs['pk'] = self.get_object().id
        kwargs['pk'] = self.kwargs.get('pk')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = None
        context['title'] = "Global scope"
        context['users'] = UserRoleTable(self.object.users)
        return context


class GlobalScopeDefaultPermissionView(SquestDetailView):
    model = GlobalScope
    template_name = "profiles/global_scope_default_permission_detail.html"

    def get_object(self, queryset=None):
        return GlobalScope.load()

    def dispatch(self, request, *args, **kwargs):
        self.kwargs['pk'] = self.get_object().id
        kwargs['pk'] = self.kwargs.get('pk')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = None
        context['title'] = "Default permissions"
        permission_table = PermissionTable(self.object.global_permissions.all())
        permission_table.exclude = ("actions",)
        context['global_permissions'] = permission_table
        owner_permission_table = PermissionTable(self.object.owner_permissions.all())
        owner_permission_table.exclude = ("actions",)
        context['owner_permissions'] = owner_permission_table
        return context


class GlobalScopeEditView(SquestUpdateView):
    model = GlobalScope
    form_class = GlobalScopeForm

    def get_object(self, queryset=None):
        return GlobalScope.load()

    def get_success_url(self):
        return reverse_lazy('profiles:globalscope_default_permissions')

    def dispatch(self, request, *args, **kwargs):
        self.kwargs['pk'] = self.get_object().id
        kwargs['pk'] = self.kwargs.get('pk')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Global scope', 'url': reverse('profiles:globalscope_rbac')},
            {'text': f'Edit', 'url': ""},
        ]
        return context
