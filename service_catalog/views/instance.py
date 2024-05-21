import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_fsm import can_proceed
from jinja2 import UndefinedError, TemplateError

from Squest.utils.squest_table import SquestRequestConfig
from Squest.utils.squest_views import SquestListView, SquestDetailView, SquestUpdateView, SquestDeleteView, \
    SquestPermissionDenied
from service_catalog.filters.instance_filter import InstanceFilter, InstanceArchivedFilter
from service_catalog.forms import InstanceForm, OperationRequestForm, SupportRequestForm, SupportMessageForm, \
    InstanceFormRestricted
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

logger = logging.getLogger(__name__)


class InstanceListViewGeneric(SquestListView):
    table_class = InstanceTable
    model = Instance

    def get_queryset(self):
        return Instance.get_queryset_for_user(
            self.request.user,
            "service_catalog.view_instance"
        ).prefetch_related(
            'requester', 'service', 'quota_scope'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['html_button_path'] = ''
        context['action_url'] = ''
        if self.request.user.has_perm("service_catalog.delete_instance"):
            context['html_button_path'] = 'generics/buttons/bulk_delete_button.html'
            context['action_url'] = reverse('service_catalog:instance_bulk_delete')
        return context


class InstanceListView(InstanceListViewGeneric):
    filterset_class = InstanceFilter

    def get_queryset(self):
        return super().get_queryset().exclude(state=InstanceState.ARCHIVED)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['extra_html_button_path'] = "service_catalog/buttons/instance-archived-list.html"
        return context


class InstanceArchivedListView(InstanceListViewGeneric):
    filterset_class = InstanceArchivedFilter

    def get_queryset(self):
        return super().get_queryset().filter(state=InstanceState.ARCHIVED)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['breadcrumbs'] = [
            {'text': 'Instances', 'url': reverse('service_catalog:instance_list')},
            {'text': 'Archived instance', 'url': ""}
        ]
        return context


class InstanceDetailView(SquestDetailView):
    model = Instance
    filterset_class = InstanceFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = SquestRequestConfig(self.request)

        # operations
        operations = Operation.objects.none()
        if self.request.user.has_perm("service_catalog.request_on_instance", self.object):
            operations = operations | self.object.service.operations.filter(is_admin_operation=False,
                                                                            enabled=True,
                                                                            type__in=[OperationType.UPDATE,
                                                                                      OperationType.DELETE])

        # admin operations
        if self.request.user.has_perm("service_catalog.admin_request_on_instance", self.object):
            operations = operations | self.object.service.operations.filter(is_admin_operation=True,
                                                                            enabled=True,
                                                                            type__in=[OperationType.UPDATE,
                                                                                      OperationType.DELETE])
        if operations.exists():
            context['operations_table'] = OperationTableFromInstanceDetails(operations, prefix="operation-")
            if not self.request.user.has_perm("service_catalog.admin_request_on_instance", self.object):
                context['operations_table'].exclude = ("is_admin_operation",)
            config.configure(context['operations_table'])

        # requests
        if self.request.user.has_perm("service_catalog.view_request", self.object):
            context['requests_table'] = RequestTable(
                self.object.request_set.distinct(),
                hide_fields=["instance", "instance__service", "selection"],
                prefix="request-"
            )
            config.configure(context['requests_table'])

        # support
        if self.request.user.has_perm("service_catalog.view_support", self.object):
            context['supports_table'] = SupportTable(
                self.object.supports.distinct(),
                hide_fields=["instance"],
                prefix="support-"
            )
            config.configure(context['supports_table'])

        # doc
        rendered_docs = list()
        for doc in self.get_object().docs:
            rendered_doc = doc.content
            try:
                rendered_doc = doc.render(self.get_object())
            except TemplateError as e:
                logger.warning(f"Error: {e.message}, instance: {self.get_object()}, doc: {doc}")
                messages.warning(self.request, f'Failure while templating documentation: {doc.title}. {e.message}')
            rendered_docs.append({
                "id": doc.id,
                "content": rendered_doc,
                "title": doc.title
            })
        context["docs"] = rendered_docs

        return context


class InstanceEditView(SquestUpdateView):
    model = Instance
    form_class = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def has_permission(self):
        try:
            obj = self.get_object()
        except AttributeError:
            obj = None
        if self.request.user.has_perm("service_catalog.change_instance", obj) or \
                self.request.user.has_perm("service_catalog.rename_instance", obj) or \
                self.request.user.has_perm("service_catalog.change_owner_instance", obj):
            return True
        return False

    def get_form_class(self):
        if self.request.user.has_perm("service_catalog.change_instance", self.object):
            return InstanceForm
        elif (self.request.user.has_perm("service_catalog.rename_instance", self.object) or
              self.request.user.has_perm("service_catalog.change_owner_instance", self.object)):
            return InstanceFormRestricted
        return None


class InstanceDeleteView(SquestDeleteView):
    model = Instance


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
    # do not allow to ask for a deletion if delete request already there
    if instance.has_pending_delete_request:
        raise PermissionDenied("A deletion request has already been submitted for this instance")

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
    # add instance so it can be used in doc templating
    rendered_docs = list()
    for doc in docs:
        rendered_doc = doc.content
        try:
            rendered_doc = doc.render(instance)
        except TemplateError as e:
            logger.warning(f"Error: {e.message}, instance: {instance}, doc: {doc}")
            messages.warning(request, f'Failure while templating documentation: {doc.title}. {e.message}')
        rendered_docs.append({
            "id": doc.id,
            "content": rendered_doc,
            "title": doc.title
        })

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
        'docs': rendered_docs
    }
    return render(request, 'service_catalog/customer/generic_list_with_docs.html', context)


@login_required
def instance_archive(request, pk):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    instance = get_object_or_404(Instance, id=pk)
    if not request.user.has_perm('service_catalog.archive_instance', instance):
        raise PermissionDenied
    if not can_proceed(instance.archive):
        raise PermissionDenied
    instance.archive()
    instance.save()
    return redirect(instance.get_absolute_url())


@login_required
def instance_unarchive(request, pk):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    instance = get_object_or_404(Instance, id=pk)
    if not request.user.has_perm('service_catalog.unarchive_instance', instance):
        raise PermissionDenied
    if not can_proceed(instance.unarchive):
        raise PermissionDenied
    instance.unarchive()
    instance.save()
    return redirect(instance.get_absolute_url())


@login_required
def support_create(request, instance_id):
    instance = get_object_or_404(Instance, id=instance_id)
    if not request.user.has_perm("service_catalog.add_support", instance):
        raise PermissionDenied
    parameters = {
        'instance_id': instance_id
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
             'url': reverse('service_catalog:instance_details', args=[instance_id])},
        ],
        'color_button': 'success',
        'text_button': 'Open new support',
        'icon_button': 'fas fa-plus'
    }
    return render(request, 'generics/generic_form.html', context)


@login_required
def support_details(request, instance_id, pk):
    instance = get_object_or_404(Instance, id=instance_id)
    support = get_object_or_404(Support, id=pk)
    if request.method == 'GET':
        if not request.user.has_perm('service_catalog.view_support', support):
            raise PermissionDenied
    if request.method == 'POST':
        if not request.user.has_perm('service_catalog.add_supportmessage', instance):
            raise PermissionDenied
        form = SupportMessageForm(request.POST or None, sender=request.user, support=support)
        if form.is_valid():

            if form.cleaned_data['content'] is not None and form.cleaned_data["content"] != "":
                form.save()
            return redirect('service_catalog:support_details', instance.id, support.id)
    else:
        form = SupportMessageForm(sender=request.user, support=support)
    context = {
        'form': form,
        'instance': instance,
        'messages': SupportMessage.objects.filter(support=support),
        'support': support,
        'breadcrumbs': [
            {'text': 'Instances', 'url': reverse('service_catalog:instance_list')},
            {'text': f'{instance.name} ({instance.id})',
             'url': reverse('service_catalog:instance_details', args=[instance_id])},
            {'text': 'Support', 'url': ''},
            {'text': support.title, 'url': ''},
        ]
    }
    return render(request, 'service_catalog/common/instance-support-details.html', context)


@login_required
def supportmessage_edit(request, instance_id, support_id, pk):
    support_message = get_object_or_404(SupportMessage, id=pk)
    if request.user != support_message.sender or not request.user.has_perm('service_catalog.change_supportmessage',
                                                                           support_message):
        raise PermissionDenied
    if request.method == "POST":
        form = SupportMessageForm(request.POST or None, request.FILES or None, sender=support_message.sender,
                                  support=support_message.support, instance=support_message)
        if form.is_valid():
            form.save()
            return redirect('service_catalog:support_details', support_message.support.instance.id,
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
             'url': reverse('service_catalog:support_details',
                            kwargs={'instance_id': instance_id, 'pk': support_id})},
        ],
        'action': 'edit'
    }
    return render(request, "generics/generic_form.html", context)


@login_required
def instance_bulk_delete(request):
    context = dict()
    context['confirm_text'] = mark_safe(f"Confirm deletion of the following instances?")
    context['action_url'] = reverse('service_catalog:instance_bulk_delete')
    context['button_text'] = 'Delete'
    context['breadcrumbs'] = [
        {'text': 'Instance', 'url': reverse('service_catalog:instance_list')},
        {'text': "Delete multiple", 'url': ""}
    ]

    if request.method == "GET":
        pks = request.GET.getlist("selection")
    if request.method == "POST":
        pks = request.POST.getlist("selection")

    context["object_list"] = Instance.get_queryset_for_user(request.user, 'service_catalog.delete_instance',
                                                            unique=False).filter(pk__in=pks)
    if context['object_list'].count() != len(pks):
        raise PermissionDenied

    if not context['object_list']:
        messages.warning(request, 'Empty selection.')
        return redirect("service_catalog:instance_list")

    if request.method == "GET":
        return render(request, 'generics/confirm-bulk-delete-template.html', context=context)

    elif request.method == "POST":
        context['object_list'].delete()
        return redirect("service_catalog:instance_list")
