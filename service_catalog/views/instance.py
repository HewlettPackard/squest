from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_fsm import can_proceed
from guardian.decorators import permission_required_or_403
from jinja2 import UndefinedError

from service_catalog.forms import InstanceForm, OperationRequestForm, SupportRequestForm, SupportMessageForm
from service_catalog.models.instance import Instance
from service_catalog.models.support import Support
from service_catalog.models.operations import Operation
from service_catalog.models.instance_state import InstanceState
from service_catalog.models.operation_type import OperationType
from service_catalog.models.message import SupportMessage
from service_catalog.models.request import Request
from service_catalog.models.documentation import Doc
from service_catalog.tables.operation_tables import OperationTableFromInstanceDetails
from service_catalog.tables.request_tables import RequestTable
from service_catalog.views.support_list_view import SupportTable


@user_passes_test(lambda u: u.is_superuser)
def instance_edit(request, instance_id):
    instance = get_object_or_404(Instance, id=instance_id)
    form = InstanceForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('service_catalog:instance_details', instance.id)
    context = {
        'form': form,
        'breadcrumbs': [
            {'text': 'Instances', 'url': reverse('service_catalog:instance_list')},
            {'text': f"{instance.name} ({instance.id})",
             'url': reverse('service_catalog:instance_details', args=[instance_id])},
        ],
        'object_name': 'instance'}
    return render(request, 'generics/edit-sensitive-object.html', context)


@user_passes_test(lambda u: u.is_superuser)
def instance_delete(request, instance_id):
    instance = get_object_or_404(Instance, id=instance_id)
    if request.method == 'POST':
        instance.delete()
        return redirect("service_catalog:instance_list")
    args = {
        "instance_id": instance_id,
    }
    context = {
        'breadcrumbs': [
            {'text': 'Instances', 'url': reverse('service_catalog:instance_list')},
            {'text': f"{instance.name} ({instance.id})",
             'url': reverse('service_catalog:instance_details', args=[instance_id])},
            {'text': 'Delete', 'url': ''}
        ],
        'confirm_text': mark_safe(f"Confirm deletion of <strong>{instance.name}</strong>?"),
        'action_url': reverse('service_catalog:instance_delete', kwargs=args),
        'button_text': 'Delete',
        'details':
            {
                'warning_sentence': 'Warning: all requests related to this instance will be deleted:',
                'details_list': [f"ID: {request.id}, State: {request.state}" for request in instance.request_set.all()]
            } if instance.request_set.count() != 0 else None
    }
    return render(request, 'generics/confirm-delete-template.html', context=context)


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
@permission_required_or_403('service_catalog.request_support_on_instance', (Instance, 'id', 'instance_id'))
def instance_new_support(request, instance_id):
    target_instance = get_object_or_404(Instance, id=instance_id)
    parameters = {
        'instance_id': instance_id
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
            {'text': f"{target_instance.name} ({target_instance.id})", 'url': reverse('service_catalog:instance_details', args=[instance_id])},
        ],
        'color_button': 'success',
        'text_button': 'Open new support',
        'icon_button': 'fas fa-plus'
    }
    return render(request, 'generics/generic_form.html', context)


@login_required
@permission_required_or_403('service_catalog.request_support_on_instance', (Instance, 'id', 'instance_id'))
def instance_support_details(request, instance_id, support_id):
    instance = get_object_or_404(Instance, id=instance_id)
    support = get_object_or_404(Support, id=support_id)
    messages = SupportMessage.objects.filter(support=support)
    if request.method == "POST":
        form = SupportMessageForm(request.POST or None, sender=request.user, support=support)
        if "btn_close" in request.POST:
            if not can_proceed(support.do_close):
                raise PermissionDenied
            support.do_close()
            support.save()
        if "btn_re_open" in request.POST:
            if not can_proceed(support.do_open):
                raise PermissionDenied
            support.do_open()
            support.save()
        if form.is_valid():
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
        form = SupportMessageForm(sender=support_message.sender, support=support_message.support, instance=support_message)
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
@permission_required_or_403('service_catalog.view_instance', (Instance, 'id', 'instance_id'))
def instance_details(request, instance_id):
    instance = get_object_or_404(Instance, id=instance_id)
    supports = Support.objects.filter(instance=instance)
    if request.user.is_superuser:
        operations = Operation.objects.filter(service=instance.service,
                                              type__in=[OperationType.UPDATE, OperationType.DELETE], enabled=True)
    else:
        operations = Operation.objects.filter(service=instance.service,
                                              type__in=[OperationType.UPDATE, OperationType.DELETE], enabled=True,
                                              is_admin_operation=False)
    requests = Request.objects.filter(instance=instance)
    operations_table = OperationTableFromInstanceDetails(operations)
    requests_table = RequestTable(requests,
                                  hide_fields=["instance__name", "instance__service__name"])
    supports_table = SupportTable(supports, hide_fields=["instance__name"])

    context = {'instance': instance,
               'operations_table': operations_table,
               'requests_table': requests_table,
               'supports_table': supports_table,
               'app_name': 'service_catalog',
               'object': instance,
               'object_name': 'instance',
               'object_id': instance.id,
               'breadcrumbs': [
                   {'text': 'Instances', 'url': reverse('service_catalog:instance_list')},
                   {'text': f"{instance.name} ({instance.id})", 'url': ""},
               ],
               }
    return render(request, 'service_catalog/common/instance-details.html', context=context)

@login_required
@permission_required_or_403('service_catalog.change_instance', (Instance, 'id', 'instance_id'))
def user_in_instance_remove(request, instance_id, user_id):
    instance = get_object_or_404(Instance, id=instance_id)
    user = User.objects.get(id=user_id)
    if user == instance.requester:
        return redirect(reverse('service_catalog:instance_details', args=[instance_id]) + "#users")
    if request.method == 'POST':
        instance.remove_user_in_role(user)
        return redirect(reverse('service_catalog:instance_details', args=[instance_id]) + "#users")
    args = {
        "instance_id": instance_id,
        "user_id": user_id
    }
    context = {
        'breadcrumbs': [
            {'text': 'Instances', 'url': reverse('service_catalog:instance_list')},
            {'text': instance.name, 'url': reverse('service_catalog:instance_details', args=[instance_id])},
            {'text': "Users", 'url': ""}
        ],
        'confirm_text': mark_safe(f"Confirm to remove all roles of the user <strong>{user.username}</strong> from "
                                  f"{instance}?"),
        'action_url': reverse('service_catalog:user_in_instance_remove', kwargs=args),
        'button_text': 'Remove'
    }
    return render(request, 'generics/confirm-delete-template.html', context=context)


@login_required
@permission_required_or_403('service_catalog.change_instance', (Instance, 'id', 'instance_id'))
def group_in_instance_remove(request, instance_id, group_id):
    instance = get_object_or_404(Instance, id=instance_id)
    group = Group.objects.get(id=group_id)
    if request.method == 'POST':
        instance.remove_group_in_role(group)
        return redirect(reverse('service_catalog:instance_details', args=[instance_id]) + "#groups")
    args = {
        "instance_id": instance_id,
        "group_id": group_id
    }
    context = {
        'breadcrumbs': [
            {'text': 'Instances', 'url': reverse('service_catalog:instance_list')},
            {'text': instance.name, 'url': reverse('service_catalog:instance_details', args=[instance_id])},
            {'text': "Groups", 'url': ""}
        ],
        'confirm_text': mark_safe(f"Confirm to remove all roles of the group <strong>{group.name}</strong> on "
                                  f"{instance}?"),
        'action_url': reverse('service_catalog:group_in_instance_remove', kwargs=args),
        'button_text': 'Remove'
    }
    return render(request, 'generics/confirm-delete-template.html', context=context)






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
