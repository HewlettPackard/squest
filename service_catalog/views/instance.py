from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_fsm import can_proceed
from jinja2 import UndefinedError

from Squest.utils.squest_views import SquestListView, SquestDetailView, SquestUpdateView, SquestDeleteView, \
    SquestPermissionDenied
from service_catalog.filters.instance_filter import InstanceFilter
from service_catalog.forms import InstanceForm, OperationRequestForm, SupportRequestForm, SupportMessageForm
from service_catalog.models.documentation import Doc
from service_catalog.models.instance import Instance
from service_catalog.models.instance_state import InstanceState
from service_catalog.models.message import SupportMessage
from service_catalog.models.operation_type import OperationType
from service_catalog.models.operations import Operation
from service_catalog.models.support import Support
from service_catalog.tables.instance_tables import InstanceTable
from service_catalog.tables.operation_tables import OperationTableFromInstanceDetails
from service_catalog.tables.request_tables import RequestTable
from service_catalog.tables.support_tables import SupportTable


class InstanceListView(SquestListView):
    table_class = InstanceTable
    model = Instance
    filterset_class = InstanceFilter

    def get_queryset(self):
        return Instance.get_queryset_for_user(self.request.user, "service_catalog.view_instance")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['html_button_path'] = ''
        context['action_url'] = ''

        if self.request.user.has_perm("service_catalog.delete_instance"):
            context['html_button_path'] = 'generics/buttons/bulk_delete_button.html'
            context['action_url'] = reverse('service_catalog:instance_bulk_delete_confirm')
        return context


class InstanceDetailView(SquestDetailView):
    model = Instance
    filterset_class = InstanceFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # operations
        operations = Operation.objects.none()
        if self.request.user.has_perm("service_catalog.request_on_instance"):
            operations = operations | self.object.service.operations.filter(is_admin_operation=False)

        # admin operations
        if self.request.user.has_perm("service_catalog.admin_request_on_instance"):
            operations = operations | self.object.service.operations.filter(is_admin_operation=True)

        context['operations_table'] = OperationTableFromInstanceDetails(operations)

        # requests
        if self.request.user.has_perm("service_catalog.view_request", self.object):
            context['requests_table'] = RequestTable(
                self.object.request_set.distinct(),
                hide_fields=["instance", "instance__service"]
            )
        # support
        if self.request.user.has_perm("service_catalog.view_support", self.object):
            context['supports_table'] = SupportTable(
                self.object.supports.distinct(),
                hide_fields=["instance"]
            )
        return context


class InstanceEditView(SquestUpdateView):
    model = Instance
    form_class = InstanceForm


class InstanceDeleteView(SquestDeleteView):
    model = Instance
    template_name = 'generics/confirm-delete-template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['confirm_text'] = mark_safe(f"Confirm deletion of <strong>{self.object.name}</strong>?")
        context['details'] = {
            'warning_sentence': 'Warning: all requests related to this instance will be deleted:',
            'details_list': [f"ID: {request.id}, State: {request.state}" for request in
                             self.object.request_set.all()]} if self.object.request_set.count() != 0 else None
        return context


@login_required
def instance_request_new_operation(request, instance_id, operation_id):
    instance = get_object_or_404(Instance, id=instance_id)
    operation = get_object_or_404(Operation, id=operation_id)
    if not operation.is_admin_operation and not request.user.has_perm('service_catalog.request_on_instance',
                                                                      instance):
        raise SquestPermissionDenied(permission='service_catalog.request_on_instance')
    if operation.is_admin_operation and not request.user.has_perm('service_catalog.admin_request_on_instance',
                                                                  instance):
        raise SquestPermissionDenied(permission="service_catalog.admin_request_on_instance")
    if instance.state not in [InstanceState.AVAILABLE]:
        raise PermissionDenied("Instance not available")
    if operation.enabled is False:
        raise PermissionDenied(f"Operation is not enabled.")
    if operation.service.id != instance.service.id:
        raise PermissionDenied("Operation service and instance service doesn't match")
    if operation.type not in [OperationType.UPDATE, OperationType.DELETE]:
        raise PermissionDenied("Operation type UPDATE and DELETE only")

    parameters = {
        'operation': operation,
        'instance': instance
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
def instance_archive(request, instance_id):
    instance = get_object_or_404(Instance, id=instance_id)
    if not request.user.has_perm('service_catalog.archive_instance', instance):
        raise PermissionDenied
    if request.method == "POST":
        if not can_proceed(instance.archive):
            raise PermissionDenied
        instance.archive()
        instance.save()

        return redirect('service_catalog:instance_list')
    context = {
        "instance": instance
    }
    return render(request, "service_catalog/instance-archive.html", context)


@login_required
def instance_new_support(request, pk):
    instance = get_object_or_404(Instance, id=pk)
    if not request.user.has_perm("service_catalog.add_support", instance):
        raise PermissionDenied
    parameters = {
        'instance_id': pk
    }

    if instance.service.external_support_url is not None and instance.service.external_support_url != '':
        from jinja2 import Template
        spec_config = {
            "instance": instance,
        }
        template_url = Template(instance.service.external_support_url)
        try:
            template_url_rendered = template_url.render(spec_config)
        except UndefinedError:
            # in case of any error we just use the given URL with the jinja so the admin can see the templating error
            template_url_rendered = instance.service.external_support_url

        return redirect(template_url_rendered)

    if request.method == 'POST':
        form = SupportRequestForm(request.user, request.POST, **parameters)
        if form.is_valid():
            form.save()
            return redirect(reverse('service_catalog:instance_details', args=[instance.id]) + "#support")
    else:
        form = SupportRequestForm(request.user, **parameters)
    context = {
        'form': form,
        'instance': instance,
        'breadcrumbs': [
            {'text': 'Instances', 'url': reverse('service_catalog:instance_list')},
            {'text': f"{instance.name} ({instance.id})",
             'url': reverse('service_catalog:instance_details', args=[pk])},
        ],
        'color_button': 'success',
        'text_button': 'Open new support',
        'icon_button': 'fas fa-plus'
    }
    return render(request, 'generics/generic_form.html', context)


@login_required
def instance_support_details(request, instance_id, support_id):
    instance = get_object_or_404(Instance, id=instance_id)
    if not request.user.has_perm('service_catalog.view_instance', instance):
        raise PermissionDenied
    support = get_object_or_404(Support, id=support_id)
    messages = SupportMessage.objects.filter(support=support)
    if request.method == "POST":
        form = SupportMessageForm(request.POST or None, sender=request.user, support=support)
        if form.is_valid():
            if not request.user.has_perm('service_catalog.add_supportmessage', instance):
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
def support_message_edit(request, instance_id, support_id, message_id):
    support_message = get_object_or_404(SupportMessage, id=message_id)
    if not request.user.has_perm('service_catalog.change_supportmessage', support_message):
        raise PermissionDenied
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


@login_required
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
        context['object_list'] = Instance.get_queryset_for_user(request.user, 'service_catalog.delete_instance').filter(
            pk__in=pks)
        if context['object_list'].count() != len(pks):
            raise PermissionDenied
        if context['object_list']:
            return render(request, 'generics/confirm-bulk-delete-template.html', context=context)
    messages.warning(request, 'No instances were selected for deletion.')
    return redirect('service_catalog:instance_list')


@login_required
def instance_bulk_delete(request):
    if request.method == "POST":
        pks = request.POST.getlist("selection")
        selected_instances = Instance.get_queryset_for_user(request.user, 'service_catalog.delete_instance').filter(
            pk__in=pks)
        if selected_instances.count() != len(pks):
            raise PermissionDenied
        selected_instances.delete()
    return redirect("service_catalog:instance_list")
