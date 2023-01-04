from operator import xor

from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe

from service_catalog.forms import ApprovalStepForm
from service_catalog.models import ApprovalWorkflow
from service_catalog.models.approval_step import ApprovalStep


@user_passes_test(lambda u: u.is_superuser)
def approval_step_create(request, approval_workflow_id):
    approval_workflow = get_object_or_404(ApprovalWorkflow, id=approval_workflow_id)
    previous_id = request.GET.get('previous_id')
    previous = get_object_or_404(ApprovalStep.objects.filter(approval_workflow=approval_workflow),
                                 id=previous_id) if previous_id else None
    if xor(bool(approval_workflow.entry_point), bool(previous_id)):
        raise PermissionDenied
    if request.method == 'POST':
        form = ApprovalStepForm(request.POST, approval_workflow_id=approval_workflow.id)
        if form.is_valid():
            approval_step = form.save()
            if previous:
                next_approval_step_id = previous.next.id if previous.next else None
                previous.set_next(approval_step.id)
                approval_step.set_next(next_approval_step_id)
            if 'next_button' in request.POST:
                return redirect(reverse('service_catalog:approval_step_create', args=[approval_workflow_id]) + "?previous_id=" + str(approval_step.id))
            return redirect('service_catalog:approval_step_graph', approval_workflow.id)
    else:
        form = ApprovalStepForm(approval_workflow_id=approval_workflow.id)
    context = {
        'form': form,
        'breadcrumbs': [
            {'text': 'Approvals', 'url': reverse('service_catalog:approval_workflow_list')},
            {'text': approval_workflow.name,
             'url': reverse('service_catalog:approval_step_graph',
                            kwargs={'approval_workflow_id': approval_workflow.id})},
            {'text': "Create a new approval step", 'url': ""}
        ],
        'custom_buttons_html': "service_catalog/admin/approval/add_approval_step.html"
    }
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def approval_step_edit(request, approval_workflow_id, approval_step_id):
    approval_workflow = get_object_or_404(ApprovalWorkflow, id=approval_workflow_id)
    approval_step = get_object_or_404(ApprovalStep, id=approval_step_id)
    form = ApprovalStepForm(request.POST or None, approval_workflow_id=approval_workflow.id, instance=approval_step)
    if form.is_valid():
        form.save()
        return redirect('service_catalog:approval_step_graph', approval_workflow.id)
    context = {'form': form,
               'approval_step': approval_step,
               'breadcrumbs': [
                   {'text': 'Approvals', 'url': reverse('service_catalog:approval_workflow_list')},
                   {'text': approval_workflow.name, 'url': reverse('service_catalog:approval_step_graph',
                                                                   kwargs={
                                                                       'approval_workflow_id': approval_workflow.id})},
                   {'text': approval_step, 'url': ""}
               ],
               'action': 'edit'
               }
    return render(request, 'generics/generic_form.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def approval_step_delete(request, approval_workflow_id, approval_step_id):
    approval_workflow = get_object_or_404(ApprovalWorkflow, id=approval_workflow_id)
    approval_step = get_object_or_404(ApprovalStep, id=approval_step_id)
    if request.method == "POST":
        approval_step.delete()
        return redirect('service_catalog:approval_step_graph', approval_workflow.id)
    context = {
        'breadcrumbs': [
            {'text': 'Approvals', 'url': reverse('service_catalog:approval_workflow_list')},
            {'text': approval_workflow.name, 'url': reverse('service_catalog:approval_step_graph',
                                                            kwargs={'approval_workflow_id': approval_workflow.id})},
            {'text': approval_step, 'url': ""}
        ],
        'confirm_text': mark_safe(f"Confirm deletion of <strong>{approval_step}</strong>?"),
        'action_url': reverse('service_catalog:approval_step_delete',
                              kwargs={
                                  'approval_workflow_id': approval_workflow.id,
                                  'approval_step_id': approval_step_id
                              }),
        'button_text': 'Delete',
        'details': None
    }
    return render(request, "generics/confirm-delete-template.html", context)


@user_passes_test(lambda u: u.is_superuser)
def approval_step_graph(request, approval_workflow_id):
    approval_workflow = get_object_or_404(ApprovalWorkflow, id=approval_workflow_id)
    if not approval_workflow.entry_point:
        return redirect('service_catalog:approval_step_create', approval_workflow_id)
    context = {
        'breadcrumbs': [
            {'text': 'Approvals', 'url': reverse('service_catalog:approval_workflow_list')},
            {'text': approval_workflow.name, 'url': ''}
        ],
        'approval_steps': approval_workflow.approval_step_list.order_by("position"),
        'approval_workflow': approval_workflow
    }
    return render(request, "service_catalog/admin/approval/approval-step-graph.html", context)
