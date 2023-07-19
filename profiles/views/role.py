from Squest.utils.squest_views import *
from profiles.filters import RoleFilter
from profiles.forms import RoleForm
from profiles.models import Role
from profiles.tables import RoleTable, PermissionTable


class RoleListView(SquestListView):
    model = Role
    filterset_class = RoleFilter
    table_class = RoleTable
    ordering = 'name'


class RoleDetailView(SquestDetailView):
    model = Role

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        permission_table = PermissionTable(self.object.permissions.all())
        permission_table.exclude = ("actions",)
        context['permissions_table'] = permission_table
        return context


class RoleCreateView(SquestCreateView):
    model = Role
    form_class = RoleForm


class RoleEditView(SquestUpdateView):
    model = Role
    form_class = RoleForm


class RoleDeleteView(SquestDeleteView):
    model = Role
