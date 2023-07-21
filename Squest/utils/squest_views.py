import traceback

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db.models import ProtectedError
from django.urls import reverse_lazy, NoReverseMatch, reverse
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, FormView
from django.views.generic.detail import SingleObjectMixin
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from Squest.utils.squest_rbac import SquestPermissionRequiredMixin


class SquestPermissionDenied(PermissionDenied):
    def __init__(self, permission, *args, **kwargs):
        self.permission = permission
        super().__init__(mark_safe(f"Permission <b>{permission}</b> required"))


class SquestView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.django_content_type = ContentType.objects.get_for_model(self.model)

    def get_generic_url_kwargs(self):
        return {}

    def get_generic_url(self, action):
        try:
            return reverse_lazy(f'{self.app_label}:{self.django_content_type.model}_{action}',
                                kwargs=self.get_generic_url_kwargs())
        except AttributeError:
            try:
                return reverse(f'{self.django_content_type.app_label}:{self.django_content_type.model}_{action}',
                                    kwargs=self.get_generic_url_kwargs())
            except NoReverseMatch:
                return '#'


class SquestListView(LoginRequiredMixin, SquestPermissionRequiredMixin, SingleTableMixin, SquestView, FilterView):
    table_pagination = {'per_page': 10}
    template_name = 'generics/list.html'

    def get_permission_required(self):
        return f"{self.django_content_type.app_label}.list_{self.django_content_type.model}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.django_content_type.name.capitalize()
        context['html_button_path'] = "generics/buttons/add_button.html"
        context['add_url'] = self.get_generic_url("create")
        context['django_content_type'] = self.django_content_type
        return context

    def get_queryset(self):
        try:
            qs = self.model.get_queryset_for_user(
                self.request.user,
                f"{self.django_content_type.app_label}.view_{self.django_content_type.model}"
            )
        except AttributeError as e:
            traceback.print_exc()
            qs = self.model.objects.all()
        return qs


class SquestCreateView(LoginRequiredMixin, SquestPermissionRequiredMixin, SquestView, CreateView):
    template_name = 'generics/generic_form.html'

    def get_permission_required(self):
        return f"{self.django_content_type.app_label}.add_{self.django_content_type.model}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['breadcrumbs'] = [
                {
                    'text': self.django_content_type.name.capitalize(),
                    'url': self.get_generic_url('list')
                },
                {
                    'text': f'New {self.django_content_type.name}',
                    'url': ""
                },
            ]
        except NoReverseMatch:
            pass
        context['action'] = "create"
        return context


class SquestUpdateView(LoginRequiredMixin, SquestPermissionRequiredMixin, SquestView, UpdateView):
    template_name = 'generics/generic_form.html'
    context_object_name = "object"

    def get_permission_required(self):
        return f"{self.django_content_type.app_label}.change_{self.django_content_type.model}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['breadcrumbs'] = [
                {
                    'text': self.django_content_type.name.capitalize(),
                    'url': self.get_generic_url('list')
                },
                {
                    'text': self.object,
                    'url': self.object.get_absolute_url()
                },
                {
                    'text': 'Edit',
                    'url': ""
                },
            ]
        except NoReverseMatch:
            pass
        context['action'] = "edit"
        return context


class SquestDeleteView(LoginRequiredMixin, SquestPermissionRequiredMixin, SquestView, DeleteView):
    template_name = 'generics/confirm-delete-template.html'
    context_object_name = "object"

    def get_permission_required(self):
        return f"{self.django_content_type.app_label}.delete_{self.django_content_type.model}"

    def get_success_url(self):
        return self.get_generic_url('list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {
                'text': self.django_content_type.name.capitalize(),
                'url': self.get_generic_url('list')
            },
            {
                'text': self.object,
                'url': self.object.get_absolute_url()
            },
            {
                'text': 'Delete',
                'url': ""
            },
        ]

        context['confirm_text'] = mark_safe(f"Confirm deletion of <strong>{self.object}</strong>?")
        context['action_url'] = self.get_generic_url("delete")
        context['button_text'] = 'Delete'
        return context

    def get_generic_url_kwargs(self):
        return {'pk': self.object.id}

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            error_message = f"{e.args[0]}"

            context = self.get_context_data(object=self.object, error_message=error_message,
                                            protected_objects=e.protected_objects)
            return self.render_to_response(context)


class SquestDetailView(LoginRequiredMixin, SquestPermissionRequiredMixin, SquestView, DetailView):
    # Django will add "request" (resp "instance") in context when using SquestDetailView on Request (resp Instance)
    # It cause conflicts with request object
    context_object_name = "object"

    def get_permission_required(self):
        return f"{self.django_content_type.app_label}.view_{self.django_content_type.model}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {
                'text': self.django_content_type.name.capitalize(),
                'url': self.get_generic_url('list')
            },
            {
                'text': f'New {self.django_content_type.name}',
                'url': ""
            },
        ]
        return context


class SquestFormView(LoginRequiredMixin, SquestPermissionRequiredMixin, SingleObjectMixin, SquestView, FormView):
    template_name = 'generics/generic_form.html'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_permission_required(self):
        return f"{self.django_content_type.app_label}.change_{self.django_content_type.model}"

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {
                'text': self.django_content_type.name.capitalize(),
                'url': self.get_generic_url('list')
            },
            {
                'text': self.object,
                'url': self.object.get_absolute_url()
            },
            {
                'text': "New",
                'url': ""
            },
        ]
        context['action'] = "edit"
        return context
