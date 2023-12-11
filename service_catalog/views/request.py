import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404, redirect
from django_fsm import can_proceed

from Squest.utils.squest_views import *
from service_catalog.filters.request_filter import RequestFilter, RequestArchivedFilter
from service_catalog.forms import RequestMessageForm
from service_catalog.forms.accept_request_forms import AcceptRequestForm
from service_catalog.forms.approve_workflow_step_form import ApproveWorkflowStepForm
from service_catalog.forms.process_request_form import ProcessRequestForm
from service_catalog.forms.request_forms import RequestForm
from service_catalog.mail_utils import send_email_request_canceled
from service_catalog.mail_utils import send_mail_request_update
from service_catalog.models import Request, RequestMessage, RequestState
from service_catalog.models.instance import InstanceState
from service_catalog.tables.request_tables import RequestTable

logger = logging.getLogger(__name__)


class RequestListViewGeneric(SquestListView):
    table_class = RequestTable
    model = Request
    ordering = '-date_submitted'

    def get_queryset(self):
        return Request.get_queryset_for_user(
            self.request.user, 'service_catalog.view_request'
        ).prefetch_related(
            "user", "operation", "instance__requester", "instance__quota_scope", "instance__service",
            "operation__service", "approval_workflow_state", "approval_workflow_state__approval_workflow",
            "approval_workflow_state__current_step",
            "approval_workflow_state__current_step__approval_step", "approval_workflow_state__approval_step_states"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.has_perm("service_catalog.delete_request"):
            context['html_button_path'] = 'generics/buttons/bulk_delete_button.html'
            context['action_url'] = reverse('service_catalog:request_bulk_delete')
        return context


class RequestListView(RequestListViewGeneric):
    filterset_class = RequestFilter

    def get_queryset(self):
        return super().get_queryset().exclude(state=RequestState.ARCHIVED)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['extra_html_button_path'] = "service_catalog/buttons/request-archived-list.html"
        return context


class RequestArchivedListView(RequestListViewGeneric):
    filterset_class = RequestArchivedFilter

    def get_queryset(self):
        return super().get_queryset().filter(state=RequestState.ARCHIVED)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Requests', 'url': reverse('service_catalog:request_list')},
            {'text': 'Archived requests', 'url': ""}
        ]
        return context


class RequestDetailView(SquestDetailView):
    model = Request

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_messages'] = RequestMessage.objects.filter(request=self.object)
        return context


class RequestEditView(SquestUpdateView):
    model = Request
    form_class = RequestForm


class RequestDeleteView(SquestDeleteView):
    model = Request


@login_required
def request_cancel(request, pk):
    target_request = get_object_or_404(Request, id=pk)
    if not request.user.has_perm('service_catalog.cancel_request', target_request):
        raise PermissionDenied
    if not can_proceed(target_request.cancel):
        raise PermissionDenied
    if request.method == "POST":
        send_email_request_canceled(target_request, user_applied_state=request.user)
        target_request.cancel()
        target_request.save()
        return redirect(target_request.get_absolute_url())
    context = {
        'breadcrumbs': [
            {'text': 'Requests', 'url': reverse('service_catalog:request_list')},
            {'text': pk, 'url': ""},
        ],
        'confirm_text': mark_safe(f"Do you want to cancel the request <strong>{target_request.id}</strong>?"),
        'action_url': reverse('service_catalog:request_cancel', kwargs={'pk': pk}),
        'button_text': 'Confirm cancel request',
        'details': {
            'warning_sentence': f"Canceling this request will delete the instance {target_request.instance.name}."
        } if target_request.instance.state == InstanceState.PENDING else None
    }
    return render(request, "generics/confirm-delete-template.html", context)


@login_required
def request_comment(request, request_id):
    target_request = get_object_or_404(Request, id=request_id)
    if not request.user.has_perm('service_catalog.add_requestmessage', target_request):
        raise PermissionDenied
    messages = RequestMessage.objects.filter(request=target_request)
    if request.method == "POST":
        form = RequestMessageForm(request.POST or None, request.FILES or None, sender=request.user,
                                  target_request=target_request)
        if form.is_valid():
            form.save()
            return redirect('service_catalog:requestmessage_create', target_request.id)
    else:
        form = RequestMessageForm(sender=request.user, target_request=target_request)
    context = {
        'form': form,
        'target_request': target_request,
        'messages': messages,
        'breadcrumbs': [
            {'text': 'Requests', 'url': reverse('service_catalog:request_list')},
            {'text': target_request, 'url': target_request.get_absolute_url()},
            {'text': "Comments", 'url': ''},
        ]
    }
    return render(request, "service_catalog/common/request-comment.html", context)


@login_required
def requestmessage_edit(request, request_id, pk):
    request_message = get_object_or_404(RequestMessage, id=pk)
    squest_request = get_object_or_404(Request, id=request_id)
    if request.user != request_message.sender or not request.user.has_perm('service_catalog.change_requestmessage',
                                                                           request_message):
        raise PermissionDenied
    if request.method == "POST":
        form = RequestMessageForm(request.POST or None, request.FILES or None, sender=request_message.sender,
                                  target_request=request_message.request, instance=request_message)
        if form.is_valid():
            form.save()
            return redirect('service_catalog:requestmessage_create', request_id)
    else:
        form = RequestMessageForm(sender=request_message.sender, target_request=request_message.request,
                                  instance=request_message)
    context = {
        'form': form,
        'breadcrumbs': [
            {'text': 'Requests', 'url': reverse('service_catalog:request_list')},
            {'text': squest_request, 'url': squest_request.get_absolute_url()},
            {'text': "Comments", 'url': ''},
        ],
        'action': 'edit'
    }
    return render(request, "generics/generic_form.html", context)


@login_required
def request_hold(request, pk):
    target_request = get_object_or_404(Request, id=pk)
    if not request.user.has_perm('service_catalog.hold_request', target_request):
        raise PermissionDenied
    if not can_proceed(target_request.on_hold):
        raise PermissionDenied
    if request.method == "POST":
        form = RequestMessageForm(request.POST or None, request.FILES or None, sender=request.user,
                                  target_request=target_request)
        if form.is_valid():
            message = form.save(send_notification=False)
            target_request.on_hold()
            target_request.save()
            send_mail_request_update(target_request, user_applied_state=request.user, message=message)
            return redirect(target_request.get_absolute_url())
    else:
        form = RequestMessageForm(sender=request.user, target_request=target_request)
    breadcrumbs = [
        {'text': 'Requests', 'url': reverse('service_catalog:request_list')},
        {'text': pk, 'url': ""},
    ]
    context = {
        'form': form,
        'target_request': target_request,
        'breadcrumbs': breadcrumbs
    }
    return render(request, "service_catalog/admin/request/request-hold.html", context)



@login_required
def request_reject(request, pk):
    target_request = get_object_or_404(Request, id=pk)
    if not request.user.has_perm('service_catalog.reject_request', target_request):
        if target_request.approval_workflow_state is not None:
            perm = target_request.approval_workflow_state.current_step.approval_step.permission.permission_str
            if not request.user.has_perm(perm, target_request):
                raise PermissionDenied
        else:
            raise PermissionDenied
    if not can_proceed(target_request.reject):
        raise PermissionDenied
    if request.method == "POST":
        form = RequestMessageForm(request.POST or None, request.FILES or None, sender=request.user,
                                  target_request=target_request)
        if form.is_valid():
            message = form.save(send_notification=False)
            # reject the current step if exist
            if target_request.approval_workflow_state is not None:
                target_request.approval_workflow_state.reject_current_step(request.user)
            # reject the request
            target_request.reject(request.user)
            target_request.save()
            send_mail_request_update(target_request, user_applied_state=request.user, message=message)
            return redirect(target_request.get_absolute_url())
    else:
        form = RequestMessageForm(sender=request.user, target_request=target_request)
    breadcrumbs = [
        {'text': 'Requests', 'url': reverse('service_catalog:request_list')},
        {'text': pk, 'url': ""},
    ]
    context = {
        'form': form,
        'target_request': target_request,
        'breadcrumbs': breadcrumbs
    }
    return render(request, "service_catalog/admin/request/request-reject.html", context)


@login_required
def request_accept(request, pk):
    target_request = get_object_or_404(Request, id=pk)
    if target_request.approval_workflow_state != None and target_request.state != RequestState.ACCEPTED:
        raise PermissionDenied
    if not request.user.has_perm('service_catalog.accept_request', target_request):
        raise PermissionDenied
    if not can_proceed(target_request.accept):
        raise PermissionDenied
    parameters = {
        'request': target_request
    }
    if request.method == 'POST':
        if 'accept_and_process' in request.POST:
            if not request.user.has_perm('service_catalog.process_request', target_request):
                raise PermissionDenied
        form = AcceptRequestForm(request.user, request.POST, **parameters)
        if form.is_valid():
            form.save()
            target_request.accept(request.user)
            target_request.refresh_from_db()
            send_mail_request_update(target_request, user_applied_state=request.user)
            if 'accept_and_process' in request.POST and not target_request.operation.auto_process:
                logger.info(f"[request_accept] request '{target_request.id}' accepted and processed "
                            f"by {request.user}")
                try_process_request(request.user, target_request)
            return redirect(target_request.get_absolute_url())
    else:
        form = AcceptRequestForm(request.user, **parameters)
    breadcrumbs = [
        {'text': 'Requests', 'url': reverse('service_catalog:request_list')},
        {'text': pk, 'url': reverse('service_catalog:request_details', args=[pk])},
    ]
    comment_messages = RequestMessage.objects.filter(request=target_request)
    context = {
        'custom_buttons_html': "service_catalog/accept_request_custom_buttons.html",
        'form': form,
        'object': target_request,
        'breadcrumbs': breadcrumbs,
        'comment_messages': comment_messages
    }
    return render(request, 'service_catalog/admin/request/request-accept.html', context=context)


@login_required
def request_process(request, pk):
    target_request = get_object_or_404(Request, id=pk)
    if not request.user.has_perm('service_catalog.process_request', target_request):
        raise PermissionDenied
    if not can_proceed(target_request.process):
        raise PermissionDenied
    error_message = ""
    parameters = {
        'request': target_request
    }
    if request.method == "POST":
        form = ProcessRequestForm(request.user, request.POST, **parameters)
        if form.is_valid():
            # get job template extra parameters
            inventory_override = form.cleaned_data.get('ask_inventory_on_launch')
            credentials_override = form.cleaned_data.get('ask_credential_on_launch')
            limit_override = form.cleaned_data.get('ask_limit_on_launch')
            tags_override = form.cleaned_data.get('ask_tags_on_launch')
            skip_tags_override = form.cleaned_data.get('ask_skip_tags_on_launch')
            verbosity_override = form.cleaned_data.get('ask_verbosity_on_launch')
            job_type_override = form.cleaned_data.get('ask_job_type_on_launch')
            diff_mode_override = form.cleaned_data.get('ask_diff_mode_on_launch')
            error_message = try_process_request(request.user,
                                                target_request,
                                                inventory_override=inventory_override,
                                                credentials_override=credentials_override,
                                                limit_override=limit_override,
                                                tags_override=tags_override,
                                                skip_tags_override=skip_tags_override,
                                                verbosity_override=verbosity_override,
                                                job_type_override=job_type_override,
                                                diff_mode_override=diff_mode_override
                                                )
            if not error_message:
                return redirect(target_request.get_absolute_url())
    else:
        form = ProcessRequestForm(request.user, **parameters)

    breadcrumbs = [
        {'text': 'Requests', 'url': reverse('service_catalog:request_list')},
        {'text': pk, 'url': reverse('service_catalog:request_details', args=[pk])},
        {'text': "Process", 'url': ""},
    ]

    context = {
        'icon_button': "fas fa-play",
        'text_button': "Process",
        'color_button': "success",
        'form': form,
        'target_request': target_request,
        'error_message': error_message,
        'breadcrumbs': breadcrumbs
    }
    return render(request, "service_catalog/admin/request/request-process.html", context)


@login_required
def request_archive(request, pk):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    target_request = get_object_or_404(Request, id=pk)
    if not request.user.has_perm('service_catalog.archive_request', target_request):
        raise PermissionDenied
    if not can_proceed(target_request.archive):
        raise PermissionDenied
    target_request.archive()
    target_request.save()
    return redirect(target_request.get_absolute_url())


@login_required
def request_unarchive(request, pk):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    target_request = get_object_or_404(Request, id=pk)
    if not request.user.has_perm('service_catalog.unarchive_request', target_request):
        raise PermissionDenied
    if not can_proceed(target_request.unarchive):
        raise PermissionDenied
    target_request.unarchive()
    target_request.save()
    return redirect(target_request.get_absolute_url())


def try_process_request(user, target_request, inventory_override=None, credentials_override=None, tags_override=None,
                        skip_tags_override=None, limit_override=None, verbosity_override=None, job_type_override=None,
                        diff_mode_override=None):
    # switch the state to processing before trying to execute the process
    target_request.process(user)
    target_request.perform_processing(inventory_override=inventory_override,
                                      credentials_override=credentials_override,
                                      tags_override=tags_override,
                                      skip_tags_override=skip_tags_override,
                                      limit_override=limit_override,
                                      verbosity_override=verbosity_override,
                                      job_type_override=job_type_override,
                                      diff_mode_override=diff_mode_override)
    target_request.save()
    send_mail_request_update(target_request, user_applied_state=user)


@login_required
def request_bulk_delete(request):
    context = dict()
    context['confirm_text'] = mark_safe(f"Confirm deletion of the following requests?")
    context['action_url'] = reverse('service_catalog:request_bulk_delete')
    context['button_text'] = 'Delete'
    context['breadcrumbs'] = [
        {'text': 'Requests', 'url': reverse('service_catalog:request_list')},
        {'text': "Delete multiple", 'url': ""}
    ]

    if request.method == "GET":
        pks = request.GET.getlist("selection")
    if request.method == "POST":
        pks = request.POST.getlist("selection")

    context['object_list'] = Request.get_queryset_for_user(request.user, 'service_catalog.delete_request',
                                                           unique=False).filter(
        pk__in=pks)

    if context['object_list'].count() != len(pks):
        raise PermissionDenied

    if not context['object_list']:
        messages.warning(request, 'Empty selection.')
        return redirect("service_catalog:request_list")

    if request.method == "GET":
        return render(request, 'generics/confirm-bulk-delete-template.html', context=context)

    elif request.method == "POST":
        context['object_list'].delete()
        return redirect("service_catalog:request_list")


class RequestReSubmitView(SquestConfirmView):
    model = Request

    def get_permission_required(self):
        if not can_proceed(self.get_object().re_submit):
            raise PermissionDenied
        return "service_catalog.re_submit_request"

    def form_valid(self, form):
        self.get_object().re_submit(save=False)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        new_workflow = self.get_object()._get_approval_workflow()
        context['confirm_text'] = mark_safe(f"Confirm reset of <strong>{self.object}</strong> ?"
                                            f"<br>It will reset approval steps")
        if new_workflow:
            context['confirm_text'] += mark_safe(f" and instantiate the workflow <strong>{new_workflow}</strong>")
        context['button_text'] = 'Reset to submitted'
        context['breadcrumbs'].append(
            {
                'text': 'Reset to submitted',
                'url': ''
            }
        )
        return context


class RequestApproveView(SquestFormView):
    template_name = 'generics/generic_form.html'
    form_class = ApproveWorkflowStepForm
    model = Request

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().approval_workflow_state is None or self.get_object().approval_workflow_state.current_step is None:
            return redirect(self.get_success_url())
        return super(RequestApproveView, self).dispatch(request, *args, **kwargs)

    def get_permission_required(self):
        return self.get_object().approval_workflow_state.current_step.approval_step.permission.permission_str

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def get_object(self, queryset=None):
        return Request.objects.get(id=self.kwargs['pk'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'target_request': self.get_object(), 'user': self.request.user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        breadcrumbs = [
            {'text': 'Requests', 'url': reverse('service_catalog:request_list')},
            {'text': self.get_object().id, 'url': self.get_object().get_absolute_url()},
            {'text': f'Approve step', 'url': ""},
        ]
        context['breadcrumbs'] = breadcrumbs
        context['action'] = "edit"
        context['icon_button'] = "fas fa-thumbs-up"
        context['text_button'] = "Approve"
        context['color_button'] = "primary"
        context['extra_html_form_bottom'] = "service_catalog/buttons/reject_button.html"
        return context
