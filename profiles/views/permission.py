from Squest.utils.squest_views import *
from profiles.filters import PermissionFilter
from profiles.forms.model_permission_form import ModelPermissionForm
from profiles.forms.permission_form import PermissionForm
from profiles.models import Permission
from profiles.tables import PermissionTable
from service_catalog.models import ApprovalStep


class PermissionListView(SquestListView):
    model = Permission
    filterset_class = PermissionFilter
    table_class = PermissionTable


class PermissionCreateView(SquestCreateView):
    model = Permission
    form_class = PermissionForm
    success_url = reverse_lazy('profiles:permission_list')


class PermissionEditView(SquestUpdateView):
    model = Permission
    form_class = PermissionForm
    success_url = reverse_lazy('profiles:permission_list')


class PermissionDeleteView(SquestDeleteView):
    model = Permission


class ApprovalStepPermissionCreateView(SquestCreateView):
    model = Permission
    form_class = ModelPermissionForm
    success_url = reverse_lazy('profiles:permission_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['content_type'] = ContentType.objects.get_for_model(ApprovalStep)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'][-1]['text'] = 'New approval step permission'
        return context
