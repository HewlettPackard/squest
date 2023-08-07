from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe

from Squest.utils.squest_views import SquestFormView, SquestDeleteView
from profiles.forms.scope_form import ScopeCreateRBACForm
from profiles.models import RBAC, Organization, GlobalPermission, AbstractScope, Team


def get_breadcrumbs_for_scope(scope):
    class_name = scope.__class__.__name__
    if isinstance(scope, GlobalPermission):
        breadcrumbs = [{'text': 'Global permission', 'url': reverse('profiles:globalpermission_rbac')}]
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


class ScopeRBACCreateView(SquestFormView):
    model = AbstractScope
    form_class = ScopeCreateRBACForm
    pk_url_kwarg = "scope_id"

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def get_permission_required(self):
        django_content_type = ContentType.objects.get_for_model(self.get_object().get_object().__class__)
        return f"{django_content_type.app_label}.add_users_{django_content_type.model}"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['scope'] = self.get_object()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = get_breadcrumbs_for_scope(self.get_object().get_object())
        context['breadcrumbs'].append({'text': f'Add RBAC', 'url': ""})
        return context


class ScopeRBACDeleteView(SquestDeleteView):
    model = AbstractScope

    def get_permission_required(self):
        django_content_type = ContentType.objects.get_for_model(self.get_object().get_object().__class__)
        return f"{django_content_type.app_label}.delete_users_{django_content_type.model}"

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
        context['breadcrumbs'] = get_breadcrumbs_for_scope(self.scope)
        context['breadcrumbs'] += [
            {'text': self.rbac.role, 'url': ""},
            {'text': "User", 'url': ""},
            {'text': self.user, 'url': ""},
        ]
        context['confirm_text'] = mark_safe(
            f"Confirm to remove <strong>{self.user}</strong> from <strong>{self.rbac.role}</strong>?")
        return context

    def delete(self, request, *args, **kwargs):
        try:
            self.get_object().get_object().remove_user_in_role(self.user, self.rbac.role)
            return HttpResponseRedirect(self.get_success_url())
        except ProtectedError as e:
            error_message = f"{e.args[0]}"
            context = self.get_context_data(object=self.object, error_message=error_message,
                                            protected_objects=e.protected_objects)
            return self.render_to_response(context)
