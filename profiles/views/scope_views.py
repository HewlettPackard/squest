from django.shortcuts import get_object_or_404, redirect, render
from django.utils.safestring import mark_safe
from django.views.generic import DetailView, UpdateView

from profiles.forms import GlobalPermissionForm
from profiles.forms.scope_form import ScopeCreateRBACForm
from profiles.models import RBAC, Organization, GlobalPermission, AbstractScope

from django.urls import reverse

from django.contrib.auth.models import User

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


def scope_rbac_create(request, scope_id):
    scope = get_object_or_404(AbstractScope, id=scope_id)
    form = ScopeCreateRBACForm(request.POST or None, scope=scope)
    scope = scope.get_object()
    class_name = scope.__class__.__name__
    if form.is_valid():
        form.save()
        return redirect(scope.get_absolute_url())
    if isinstance(scope, GlobalPermission):
        breadcrumbs = [
            {'text': 'Global permission', 'url': reverse('profiles:globalpermission_details')},
            {'text': f'Add RBAC', 'url': ""},
        ]
    else:
        breadcrumbs = [
            {'text': class_name, 'url': reverse(f'profiles:{class_name.lower()}_list')},
            {'text': scope,
            'url': reverse(f'profiles:{class_name.lower()}_details', kwargs={"pk": scope.id})},
            {'text': f'Add RBAC', 'url': ""},
        ]
    context = {'form': form, 'object_name': "billing_group", 'breadcrumbs': breadcrumbs,
               'action': "edit"}
    return render(request, 'generics/generic_form.html', context)


def scope_rbac_delete(request, scope_id, role_id, user_id):
    scope = get_object_or_404(AbstractScope, id=scope_id)
    scope = scope.get_object()
    rbac = get_object_or_404(RBAC, role__id=role_id, scope__id=scope_id)
    user = get_object_or_404(User, id=user_id)
    class_name = scope.__class__.__name__
    details = None
    if isinstance(scope, Organization):
        team_name_list = RBAC.objects.filter(
            scope__in=scope.teams.all(),
            user__id=user_id
        ).values_list("scope__name", flat=True)
        details = {
            'warning_sentence': 'Warning: User still in following Teams, it will be removed from them:',
            'details_list': [f"{team}," for team in team_name_list]
        } if team_name_list else None

    if request.method == 'POST':
        scope.remove_user_in_role(user, rbac.role.name)
        return redirect(scope.get_absolute_url())
    if isinstance(scope, GlobalPermission):
        breadcrumbs = [
            {'text': 'Global permission', 'url': reverse('profiles:globalpermission_details')},
            {'text': rbac.role, 'url': ""},
            {'text': "User", 'url': ""},
            {'text': user, 'url': ""},
        ]
    else:
        breadcrumbs = [
            {'text': class_name, 'url': reverse(f'profiles:{class_name.lower()}_list')},
            {'text': scope,
             'url': reverse(f'profiles:{class_name.lower()}_details', kwargs={"pk": scope.id})},
            {'text': "Role", 'url': ""},
            {'text': rbac.role, 'url': ""},
            {'text': "User", 'url': ""},
            {'text': user, 'url': ""},
        ]
    context = {
        'breadcrumbs': breadcrumbs,
        'action_url': reverse(f'profiles:{class_name.lower()}_rbac_delete',
                              kwargs={"scope_id": scope.id, "role_id": role_id, "user_id": user_id}) + "#users",
        'confirm_text': mark_safe(f"Confirm to remove <strong>{user}</strong> from <strong>{rbac.role}</strong>?"),
        'button_text': 'Delete',
        'details': details
    }
    return render(request, 'generics/confirm-delete-template.html', context=context)
