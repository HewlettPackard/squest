from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
from django.views.generic import FormView, DeleteView

from profiles.forms.scope_form import ScopeCreateRBACForm
from profiles.models import RBAC, Organization, GlobalPermission, AbstractScope, Team
from django.urls import reverse
from django.contrib.auth.models import User


def get_breadcrumbs_for_scope(scope):
    class_name = scope.__class__.__name__
    if isinstance(scope, GlobalPermission):
        breadcrumbs = [{'text': 'Global permission', 'url': reverse('profiles:globalpermission_details')}]
    else:
        breadcrumbs = [
            {'text': class_name, 'url': reverse(f'profiles:{class_name.lower()}_list')},
            {'text': scope.name, 'url': scope.get_absolute_url()},
        ]
        if isinstance(scope, Team):
            breadcrumbs = [
                              {'text': "Organization", 'url': reverse(f'profiles:organization_list')},
                              {'text': scope.org, 'url': scope.org.get_absolute_url()},
                          ] + breadcrumbs
    return breadcrumbs


class ScopeRBACCreateView(FormView):
    model = Team
    template_name = 'generics/generic_form.html'
    form_class = ScopeCreateRBACForm

    def get_success_url(self):
        return self.scope.get_absolute_url()

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.scope = get_object_or_404(AbstractScope, id=self.kwargs.get('scope_id'))
        kwargs['scope'] = self.scope
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scope = self.scope.get_object()
        breadcrumbs = get_breadcrumbs_for_scope(scope)
        breadcrumbs.append({'text': f'Add RBAC', 'url': ""})
        context['breadcrumbs'] = breadcrumbs

        context['action'] = "edit"
        return context


class ScopeRBACDeleteView(DeleteView):
    model = AbstractScope
    template_name = 'generics/confirm-delete-template.html'

    def get_object(self, queryset=None):
        abstract_scope = super().get_object(queryset)
        self.scope = abstract_scope.get_object()
        self.rbac = get_object_or_404(RBAC, role__id=self.kwargs.get('role_id'), scope__id=self.kwargs.get('pk'))
        self.user = get_object_or_404(User, id=self.kwargs.get('user_id'))
        return abstract_scope

    def get_success_url(self):
        return self.scope.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if isinstance(self.scope, Organization):
            team_name_list = RBAC.objects.filter(
                scope__in=self.scope.teams.all(),
                user__id=self.kwargs.get('user_id')
            ).values_list("scope__name", flat=True)
            context['details'] = {
                'warning_sentence': 'Warning: User still in following Teams, it will be removed from them:',
                'details_list': [f"{team}," for team in team_name_list]
            } if team_name_list else None

        context['breadcrumbs'] = get_breadcrumbs_for_scope(self.scope) + [
            {'text': self.rbac.role, 'url': ""},
            {'text': "User", 'url': ""},
            {'text': self.user, 'url': ""},
        ]
        context['confirm_text'] = mark_safe(
            f"Confirm to remove <strong>{self.user}</strong> from <strong>{self.rbac.role}</strong>?")
        return context

    def delete(self, request, *args, **kwargs):
        try:
            self.get_object().get_object().remove_user_in_role(self.user, self.rbac.role.name)
            return HttpResponseRedirect(self.get_success_url())
        except ProtectedError as e:
            error_message = f"{e.args[0]}"

            context = self.get_context_data(object=self.object, error_message=error_message,
                                            protected_objects=e.protected_objects)
            return self.render_to_response(context)
