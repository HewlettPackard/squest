from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from Squest.utils.squest_views import SquestListView
from service_catalog.filters.approval_workflow_filter import ApprovalWorkflowFilter
from service_catalog.forms.approval_workflow_form import ApprovalWorkflowForm
from service_catalog.models import ApprovalWorkflow
from service_catalog.tables.approval_workflow_table import ApprovalWorkflowTable


class ApprovalWorkflowListView(SquestListView):
    table_pagination = {'per_page': 10}
    table_class = ApprovalWorkflowTable
    model = ApprovalWorkflow
    template_name = 'generics/list.html'
    filterset_class = ApprovalWorkflowFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['html_button_path'] = "generics/buttons/add_button.html"
        return context


class ApprovalWorkflowDetailView(DetailView):
    model = ApprovalWorkflow

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Breadcrumbs
        breadcrumbs = [
            {'text': 'Approval workflow', 'url': reverse('service_catalog:approvalworkflow_list')},
            {'text': f'{self.object}', 'url': ''}
        ]
        context['breadcrumbs'] = breadcrumbs
        return context


class ApprovalWorkflowCreateView(CreateView):
    model = ApprovalWorkflow
    template_name = 'generics/generic_form.html'
    form_class = ApprovalWorkflowForm

    def get_success_url(self):
        return reverse('service_catalog:approvalworkflow_details', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = "create"
        context["breadcrumbs"] = [
            {'text': 'Approval workflow', 'url': reverse('service_catalog:approvalworkflow_list')},
            {'text': 'New approval workflow', 'url': ""},
        ]
        return context


class ApprovalWorkflowEditView(UpdateView):
    model = ApprovalWorkflow
    template_name = 'generics/generic_form.html'
    form_class = ApprovalWorkflowForm

    def get_success_url(self):
        return reverse('service_catalog:approvalworkflow_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit approval workflow'
        context['action'] = "edit"
        context["breadcrumbs"] = [
            {'text': 'Approval workflow', 'url': reverse('service_catalog:approvalworkflow_list')},
            {'text': self.object.name, 'url': ""},
        ]
        return context


class AttributeDefinitionDeleteView(DeleteView):
    model = ApprovalWorkflow
    template_name = 'generics/delete.html'
    success_url = reverse_lazy('service_catalog:approvalworkflow_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            {'text': 'Approval workflow', 'url': reverse('service_catalog:approvalworkflow_list')},
            {'text': self.object.name, 'url': ""},
        ]
        return context
