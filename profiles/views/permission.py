from django.contrib.auth.models import Permission

from Squest.utils.squest_views import *
from profiles.filters import PermissionFilter
from profiles.forms.permission_form import PermissionForm
from profiles.tables import PermissionTable


class PermissionListView(SquestListView):
    model = Permission
    filterset_class = PermissionFilter
    table_class = PermissionTable
    ordering = 'name'
    app_label = "profiles"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['html_button_path'] = "profiles/button/permission_add_button.html"
        return context


class PermissionCreateView(SquestCreateView):
    model = Permission
    form_class = PermissionForm
    app_label = "profiles"


class PermissionEditView(SquestUpdateView):
    model = Permission
    form_class = PermissionForm
    success_url = reverse_lazy('profiles:permission_list')
    app_label = "profiles"


class PermissionDeleteView(SquestDeleteView):
    model = Permission
    app_label = "profiles"
