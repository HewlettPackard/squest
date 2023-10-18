from django_tables2 import RequestConfig

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
        config = RequestConfig(self.request)
        context['breadcrumbs'] = None
        context['title'] = "Global scope"
        context['users'] = UserRoleTable(self.object.users, prefix="user-")
        config.configure(context['users'])

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
        config = RequestConfig(self.request)
        context['breadcrumbs'] = None
        context['title'] = "Default permissions"
        context['global_permissions'] = PermissionTable(self.object.global_permissions.all(), exclude='actions',
                                                        prefix="global_permissions-")
        config.configure(context['global_permissions'])
        context['owner_permissions'] = PermissionTable(self.object.owner_permissions.all(), exclude='actions',
                                                       prefix="owner_permissions-")
        config.configure(context['owner_permissions'])
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
