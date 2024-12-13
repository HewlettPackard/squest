from django.shortcuts import get_object_or_404, redirect
from formtools.wizard.views import SessionWizardView

from Squest.utils.squest_rbac import SquestPermissionRequiredMixin
from profiles.models import Scope
from service_catalog.models import Service, OperationType, Doc, Operation


class ServiceRequestWizardView(SquestPermissionRequiredMixin, SessionWizardView):

    def get_permission_required(self):
        service_id = self.kwargs['service_id']
        operation_id = self.kwargs['operation_id']
        self.operation = get_object_or_404(Operation, enabled=True, service__enabled=True, id=operation_id, type=OperationType.CREATE, service__id=service_id)
        return self.operation.permission.permission_str


    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if self.steps.current == '1':
            docs = Doc.objects.filter(operations__in=[self.operation])
            context.update({'docs': docs})
        context["title"] = f"Request - {self.operation}"
        return context

    def get_form_kwargs(self, step):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        kwargs.update({'operation': self.operation})

        if step == "1":
            # add data from step 0
            scope_id = self.storage.data['step_data']['0']['0-quota_scope'][0]
            instance_name = self.storage.data['step_data']['0']['0-name'][0]
            quota_scope = get_object_or_404(Scope, id=scope_id)
            kwargs.update({'quota_scope': quota_scope})
            kwargs.update({'instance_name': instance_name})
        return kwargs

    def get_template_names(self):
        return "service_catalog/generic_form_multiple_step.html"

    def done(self, form_list, **kwargs):
        # get data from the first form
        new_instance = form_list[0].save()
        # get data from the second form
        form_list[1].save(new_instance)
        return redirect('service_catalog:request_list')