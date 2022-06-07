from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe

from service_catalog.forms import ApprovalWorkflowForm
from service_catalog.models.approval_workflow import ApprovalWorkflow


@user_passes_test(lambda u: u.is_superuser)
def approval_workflow_create(request):
    if request.method == 'POST':
        form = ApprovalWorkflowForm(request.POST)
        if form.is_valid():
            approval_workflow = form.save()
            return redirect('service_catalog:approval_step_create', approval_workflow.id)
    else:
        form = ApprovalWorkflowForm()
    breadcrumbs = [
        {'text': 'Approvals', 'url': reverse('service_catalog:approval_workflow_list')},
        {'text': "Create a new approval workflow", 'url': ""}
    ]
    context = {
        'form': form,
        'breadcrumbs': breadcrumbs,
        'icon_button': "fas fa-arrow-right",
        'text_button': "Next",
        'color_button': "primary"
    }
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def approval_workflow_edit(request, approval_workflow_id):
    approval_workflow = get_object_or_404(ApprovalWorkflow, id=approval_workflow_id)
    form = ApprovalWorkflowForm(request.POST or None, instance=approval_workflow)
    if form.is_valid():
        form.save()
        return redirect('service_catalog:approval_workflow_list')
    breadcrumbs = [
        {'text': 'Approvals', 'url': reverse('service_catalog:approval_workflow_list')},
        {'text': approval_workflow.id, 'url': ""}
    ]
    context = {'form': form,
               'approval_workflow': approval_workflow,
               'breadcrumbs': breadcrumbs,
               'action': 'edit'
               }
    return render(request, 'generics/generic_form.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def approval_workflow_delete(request, approval_workflow_id):
    approval_workflow = get_object_or_404(ApprovalWorkflow, id=approval_workflow_id)
    if request.method == "POST":
        approval_workflow.delete()
        return redirect('service_catalog:approval_workflow_list')
    breadcrumbs = [
        {'text': 'Approvals', 'url': reverse('service_catalog:approval_workflow_list')},
        {'text': approval_workflow.id, 'url': ""}
    ]
    context = {
        'breadcrumbs': breadcrumbs,
        'confirm_text': mark_safe(f"Confirm deletion of <strong>{approval_workflow.id}</strong>?"),
        'action_url': reverse('service_catalog:approval_workflow_delete', args=[approval_workflow_id]),
        'button_text': 'Delete',
        'details': None
    }
    return render(request, "generics/confirm-delete-template.html", context)
