import json

from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, DeleteView

from service_catalog.forms.approval_step_form import ApprovalStepForm
from service_catalog.models import ApprovalStep, ApprovalWorkflow


class ApprovalStepCreateView(CreateView):
    model = ApprovalStep
    template_name = 'generics/generic_form.html'
    form_class = ApprovalStepForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['approval_workflow'] = get_object_or_404(ApprovalWorkflow, id=self.kwargs.get("approval_workflow_id"))
        return kwargs

    def get_success_url(self):
        approval_workflow_id = self.kwargs.get('approval_workflow_id')
        return reverse('service_catalog:approvalworkflow_details', kwargs={'pk': approval_workflow_id})

    def get_context_data(self, **kwargs):
        approval_workflow_id = self.kwargs.get('approval_workflow_id')
        approval_workflow = get_object_or_404(ApprovalWorkflow, id=approval_workflow_id)
        context = super().get_context_data(**kwargs)
        context['action'] = "create"
        context["breadcrumbs"] = [
            {'text': 'Approval workflow', 'url': reverse('service_catalog:approvalworkflow_list')},
            {'text': f"{approval_workflow.name}", 'url': reverse('service_catalog:approvalworkflow_details',
                                                                 kwargs={"pk": approval_workflow.id})},
            {'text': 'New step', 'url': ""},
        ]
        return context


@login_required
@permission_required('service_catalog.change_approvalstep')
def ajax_approval_step_position_update(request):
    if request.method == 'POST':
        list_step_to_update = json.loads(request.POST["listStepToUpdate"])
        for step in list_step_to_update:
            step_to_update = ApprovalStep.objects.filter(id=step["id"])
            if step_to_update.exists():
                step_to_update = step_to_update.first()
                step_to_update.position = step["position"]
                step_to_update.save()
        return JsonResponse({"update_success": True}, status=202)


class ApprovalStepEditView(UpdateView):
    model = ApprovalStep
    template_name = 'generics/generic_form.html'
    form_class = ApprovalStepForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['approval_workflow'] = get_object_or_404(ApprovalWorkflow, id=self.kwargs.get("approval_workflow_id"))
        return kwargs

    def get_success_url(self):
        approval_workflow_id = self.kwargs.get('approval_workflow_id')
        return reverse('service_catalog:approvalworkflow_details', kwargs={'pk': approval_workflow_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        approval_workflow_id = self.kwargs.get('approval_workflow_id')
        approval_workflow = get_object_or_404(ApprovalWorkflow, id=approval_workflow_id)
        context['title'] = f'Edit approval step'
        context['action'] = "edit"
        context["breadcrumbs"] = [
            {'text': 'Approval workflow', 'url': reverse('service_catalog:approvalworkflow_list')},
            {'text': f"{self.object.approval_workflow.name}", 'url': reverse('service_catalog:approvalworkflow_details',
                                                                             kwargs={"pk": approval_workflow.id})},
            {'text': f"{self.object.name}", 'url': ""},
        ]
        return context


class ApprovalStepDeleteView(DeleteView):
    model = ApprovalStep
    template_name = 'generics/delete.html'

    def get_success_url(self):
        approval_workflow_id = self.kwargs.get('approval_workflow_id')
        return reverse('service_catalog:approvalworkflow_details', kwargs={'pk': approval_workflow_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        approval_workflow_id = self.kwargs.get('approval_workflow_id')
        approval_workflow = get_object_or_404(ApprovalWorkflow, id=approval_workflow_id)
        context["breadcrumbs"] = [
            {'text': 'Approval workflow', 'url': reverse('service_catalog:approvalworkflow_list')},
            {'text': f"{self.object.approval_workflow.name}", 'url': reverse('service_catalog:approvalworkflow_details',
                                                                             kwargs={"pk": approval_workflow.id})},
            {'text': f"{self.object.name}", 'url': ""},
        ]
        return context
