from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import ProtectedError
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.generic import DetailView, UpdateView, DeleteView
from django_fsm import can_proceed
from guardian.decorators import permission_required_or_403
from jinja2 import UndefinedError
from rest_framework.reverse import reverse_lazy

from Squest.utils.squest_rbac import SquestObjectPermissions, SquestPermissionRequiredMixin
from Squest.utils.squest_views import SquestListView
from service_catalog.filters.instance_filter import InstanceFilter
from service_catalog.forms import InstanceForm, OperationRequestForm, SupportRequestForm, SupportMessageForm
from service_catalog.models.instance import Instance
from service_catalog.models.support import Support
from service_catalog.models.operations import Operation
from service_catalog.models.instance_state import InstanceState
from service_catalog.models.operation_type import OperationType
from service_catalog.models.message import SupportMessage
from service_catalog.models.documentation import Doc
from service_catalog.tables.instance_tables import InstanceTable
from service_catalog.tables.operation_tables import OperationTableFromInstanceDetails
from service_catalog.tables.request_tables import RequestTable
from service_catalog.views.support_list_view import SupportTable


class InstanceListView(SquestListView):
    table_pagination = {'per_page': 10}
    table_class = InstanceTable
    model = Instance
    template_name = 'generics/list.html'
    filterset_class = InstanceFilter

    def get_table_data(self, **kwargs):
        filtered = super().get_table_data().distinct()
        return Instance.get_queryset_for_user(
            self.request.user,
            'service_catalog.view_instance').distinct().order_by("-date_available") & filtered

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context['html_button_path'] = 'generics/buttons/delete_button.html'
            context['action_url'] = reverse('service_catalog:instance_bulk_delete_confirm')
        return context


class InstanceDetailView(LoginRequiredMixin, SquestPermissionRequiredMixin, DetailView):
    model = Instance
    filterset_class = InstanceFilter
    permission_required = "service_catalog.view_instance"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
                                     {'text': 'Instances', 'url': reverse('service_catalog:instance_list')},
                                     {'text': f"{self.object.name} ({self.object.id})", 'url': ""},
                                 ],
        context['instance'] = self.object
        context['operations_table'] = OperationTableFromInstanceDetails(self.object.service.operations.all())
        context['requests_table'] = RequestTable(self.object.request_set.all(),
                                                 hide_fields=["instance__name", "instance__service__name"])
        context['supports_table'] = SupportTable(self.object.supports.all(), hide_fields=["instance__name"])
        return context


class InstanceEditView(SquestPermissionRequiredMixin, UpdateView):
    model = Instance
    template_name = 'generics/generic_form.html'
    form_class = InstanceForm

    permission_required = "service_catalog.change_instance"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        breadcrumbs = [
            {'text': 'Instances', 'url': reverse('service_catalog:instance_list')},
            {'text': f"{self.object.name} ({self.object.id})",
             'url': self.object.get_absolute_url()},
        ]
        context['breadcrumbs'] = breadcrumbs

        context['action'] = "edit"
        return context


class InstanceDeleteView(SquestPermissionRequiredMixin, DeleteView):
    model = Instance
    template_name = 'generics/confirm-delete-template.html'
    success_url = reverse_lazy("service_catalog:instance_list")
    permission_required = "service_catalog.delete_instance"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Instances', 'url': reverse('service_catalog:instance_list')},
            {'text': f'{self.object}', 'url': ""},
        ]
        context['confirm_text'] = mark_safe(f"Confirm deletion of <strong>{self.object.name}</strong>?")
        context['details'] = {
            'warning_sentence': 'Warning: all requests related to this instance will be deleted:',
            'details_list': [f"ID: {request.id}, State: {request.state}" for request in
                             self.object.request_set.all()]} if self.object.request_set.count() != 0 else None
        return context

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            error_message = f"{e.args[0]}"

            context = self.get_context_data(object=self.object, error_message=error_message,
                                            protected_objects=e.protected_objects)
            return self.render_to_response(context)


@login_required
@permission_required_or_403('service_catalog.request_operation_on_instance', (Instance, 'id', 'instance_id'))
def instance_request_new_operation(request, instance_id, operation_id):
    instance = get_object_or_404(Instance, id=instance_id)
    if instance.state not in [InstanceState.AVAILABLE, InstanceState.UPDATING]:
        raise PermissionDenied
    operation = get_object_or_404(Operation, id=operation_id)
    allowed_operations = Operation.objects.filter(service=instance.service, enabled=True,
                                                  type__in=[OperationType.UPDATE, OperationType.DELETE])
    if operation.is_admin_operation and not request.user.is_superuser:
        raise PermissionDenied
    if operation not in allowed_operations:
        raise PermissionDenied
    parameters = {
        'operation_id': operation_id,
        'instance_id': instance_id
    }
    if request.method == 'POST':
        form = OperationRequestForm(request.user, request.POST, **parameters)
        if form.is_valid():
            form.save()
            return redirect('service_catalog:request_list')
    else:
        form = OperationRequestForm(request.user, **parameters)
    docs = Doc.objects.filter(operations__in=[operation])
    context = {
        'form': form,
        'operation': operation,
        'instance': instance,
        'breadcrumbs': [
            {'text': 'Instances', 'url': reverse('service_catalog:instance_list')},
            {'text': f"{instance.name} ({instance.id})",
             'url': reverse('service_catalog:instance_details', args=[instance_id])},
            {'text': f"Operation - {operation.name}", 'url': ''}
        ],
        'icon_button': "fas fa-shopping-cart",
        'text_button': "Request the operation",
        'color_button': "success",
        'docs': docs
    }
    return render(request, 'service_catalog/customer/generic_list_with_docs.html', context)


@login_required
@permission_required_or_403('service_catalog.delete_instance', (Instance, 'id', 'instance_id'))
def instance_archive(request, instance_id):
    target_instance = get_object_or_404(Instance, id=instance_id)
    if request.method == "POST":
        if not can_proceed(target_instance.archive):
            raise PermissionDenied
        target_instance.archive()
        target_instance.save()

        return redirect('service_catalog:instance_list')
    context = {
        "instance": target_instance
    }
    return render(request, "service_catalog/customer/instance/instance-archive.html", context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def instance_new_support(request, pk):
    target_instance = get_object_or_404(Instance, id=pk)
    parameters = {
        'instance_id': pk
    }

    if target_instance.service.external_support_url is not None and target_instance.service.external_support_url != '':
        from jinja2 import Template
        spec_config = {
            "instance": target_instance,
        }
        template_url = Template(target_instance.service.external_support_url)
        try:
            template_url_rendered = template_url.render(spec_config)
        except UndefinedError:
            # in case of any error we just use the given URL with the jinja so the admin can see the templating error
            template_url_rendered = target_instance.service.external_support_url

        return redirect(template_url_rendered)

    if request.method == 'POST':
        form = SupportRequestForm(request.user, request.POST, **parameters)
        if form.is_valid():
            form.save()
            return redirect(reverse('service_catalog:instance_details', args=[target_instance.id]) + "#support")
    else:
        form = SupportRequestForm(request.user, **parameters)
    context = {
        'form': form,
        'instance': target_instance,
        'breadcrumbs': [
            {'text': 'Instances', 'url': reverse('service_catalog:instance_list')},
            {'text': f"{target_instance.name} ({target_instance.id})",
             'url': reverse('service_catalog:instance_details', args=[pk])},
        ],
        'color_button': 'success',
        'text_button': 'Open new support',
        'icon_button': 'fas fa-plus'
    }
    return render(request, 'generics/generic_form.html', context)


@login_required
@permission_required_or_403('service_catalog.view_support', (Instance, 'id', 'instance_id'))
def instance_support_details(request, instance_id, support_id):
    instance = get_object_or_404(Instance, id=instance_id)
    support = get_object_or_404(Support, id=support_id)
    messages = SupportMessage.objects.filter(support=support)
    if request.method == "POST":
        form = SupportMessageForm(request.POST or None, sender=request.user, support=support)
        if form.is_valid():
            if not request.user.has_perm("service_catalog.comment_support", support):
                raise PermissionDenied
            if form.cleaned_data["content"] is not None and form.cleaned_data["content"] != "":
                form.save()
            return redirect('service_catalog:instance_support_details', instance.id, support.id)
    else:
        form = SupportMessageForm(sender=request.user, support=support)
    context = {
        "form": form,
        "instance": instance,
        "messages": messages,
        "support": support,
        'breadcrumbs': [
            {'text': 'Instances', 'url': reverse('service_catalog:instance_list')},
            {'text': f"{instance.name} ({instance.id})",
             'url': reverse('service_catalog:instance_details', args=[instance_id])},
            {'text': 'Support', 'url': ""},
            {'text': support.title, 'url': ""},
        ]
    }
    return render(request, "service_catalog/common/instance-support-details.html", context)


@login_required
@permission_required_or_403('service_catalog.request_support_on_instance', (Instance, 'id', 'instance_id'))
def support_message_edit(request, instance_id, support_id, message_id):
    if request.user.is_superuser:
        support_message = get_object_or_404(SupportMessage, id=message_id)
    else:
        support_message = get_object_or_404(SupportMessage, id=message_id, sender=request.user)
    if request.method == "POST":
        form = SupportMessageForm(request.POST or None, request.FILES or None, sender=support_message.sender,
                                  support=support_message.support, instance=support_message)
        if form.is_valid():
            form.save()
            return redirect('service_catalog:instance_support_details', support_message.support.instance.id,
                            support_message.support.id)
    else:
        form = SupportMessageForm(sender=support_message.sender, support=support_message.support,
                                  instance=support_message)
    context = {
        'form': form,
        'breadcrumbs': [
            {'text': 'Instances', 'url': reverse('service_catalog:instance_list')},
            {'text': f"{support_message.support.instance.name} ({support_message.support.instance.id})",
             'url': reverse('service_catalog:instance_details', args=[instance_id])},
            {'text': 'Support', 'url': ""},
            {'text': support_message.support.title,
             'url': reverse('service_catalog:instance_support_details',
                            kwargs={'instance_id': instance_id, 'support_id': support_id})},
        ],
        'action': 'edit'
    }
    return render(request, "generics/generic_form.html", context)


@user_passes_test(lambda u: u.is_superuser)
def instance_bulk_delete_confirm(request):
    context = {
        'confirm_text': mark_safe(f"Confirm deletion of the following instances?"),
        'action_url': reverse('service_catalog:instance_bulk_delete'),
        'button_text': 'Delete',
        'breadcrumbs': [
            {'text': 'Instance', 'url': reverse('service_catalog:instance_list')},
            {'text': "Delete multiple", 'url': ""}
        ]}
    if request.method == "POST":
        pks = request.POST.getlist("selection")
        context['object_list'] = Instance.objects.filter(pk__in=pks)
        if context['object_list']:
            return render(request, 'generics/confirm-bulk-delete-template.html', context=context)
    messages.warning(request, 'No instances were selected for deletion.')
    return redirect('service_catalog:instance_list')


@user_passes_test(lambda u: u.is_superuser)
def instance_bulk_delete(request):
    if request.method == "POST":
        pks = request.POST.getlist("selection")
        selected_instances = Instance.objects.filter(pk__in=pks)
        selected_instances.delete()
    return redirect("service_catalog:instance_list")
