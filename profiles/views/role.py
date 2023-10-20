from Squest.utils.squest_table import SquestRequestConfig

from Squest.utils.squest_views import *
from profiles.filters import RoleFilter
from profiles.forms import RoleForm
from profiles.models import Role
from profiles.tables import RoleTable, PermissionTable, RoleAssignementUserTable, RoleAssignementScopeTable


class RoleListView(SquestListView):
    model = Role
    filterset_class = RoleFilter
    table_class = RoleTable
    ordering = 'name'


class RoleDetailView(SquestDetailView):
    model = Role

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = SquestRequestConfig(self.request)

        context['permissions_table'] = PermissionTable(self.object.permissions.prefetch_related("content_type"),
                                                       exclude='actions', prefix="permission-")
        config.configure(context['permissions_table'])

        context['rbac_assignement_user_table'] = RoleAssignementUserTable(self.object.get_role_assignment_user_dict(),
                                                                          prefix="user-")
        config.configure(context['rbac_assignement_user_table'])

        context['rbac_assignement_scope_table'] = RoleAssignementScopeTable(
            self.object.get_role_assignment_scope_dict(), prefix="scope-")
        config.configure(context['rbac_assignement_scope_table'])
        return context


class RoleCreateView(SquestCreateView):
    model = Role
    form_class = RoleForm


class RoleEditView(SquestUpdateView):
    model = Role
    form_class = RoleForm


class RoleDeleteView(SquestDeleteView):
    model = Role
