from django.contrib.auth.models import Permission

from Squest.utils.squest_views import *
from profiles.filters import PermissionFilter
from profiles.forms.model_permission_form import ModelPermissionForm
from profiles.forms.permission_form import PermissionForm
from profiles.tables import PermissionTable
from service_catalog.models import ApprovalStep


class PermissionListView(SquestListView):
    model = Permission
    filterset_class = PermissionFilter
    table_class = PermissionTable
    ordering = 'name'
    app_label = "profiles"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['html_button_path'] = "profiles/buttons/permission_add_button.html"
        return context


class PermissionCreateView(SquestCreateView):
    model = Permission
    form_class = PermissionForm
    app_label = "profiles"
    success_url = reverse_lazy('profiles:permission_list')


class PermissionEditView(SquestUpdateView):
    model = Permission
    form_class = PermissionForm
    success_url = reverse_lazy('profiles:permission_list')
    app_label = "profiles"


class PermissionDeleteView(SquestDeleteView):
    model = Permission
    app_label = "profiles"


class ApprovalStepPermissionCreateView(SquestCreateView):
    model = Permission
    form_class = ModelPermissionForm
    app_label = "profiles"
    success_url = reverse_lazy('profiles:permission_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['content_type'] = ContentType.objects.get_for_model(ApprovalStep)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'][-1]['text'] = 'New approval step permission'
        return context
