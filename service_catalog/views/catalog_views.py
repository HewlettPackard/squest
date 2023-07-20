from django.shortcuts import get_object_or_404, redirect
from formtools.wizard.views import SessionWizardView

from Squest.utils.squest_rbac import SquestPermissionRequiredMixin
from profiles.models import Scope
from service_catalog.models import Service, OperationType, Instance, Operation, Request, RequestMessage

EXCLUDED_SURVEY_FIELDS = ["request_comment"]


class ServiceRequestWizardView(SquestPermissionRequiredMixin, SessionWizardView):

    def get_permission_required(self):
        service_id = self.kwargs['service_id']
        operation_id = self.kwargs['operation_id']
        self.service = get_object_or_404(Service, **{'id': service_id, 'enabled': True})
        self.operation = get_object_or_404(
            self.service.operations.filter(enabled=True, type=OperationType.CREATE),
            id=operation_id
        )
        if self.operation.is_admin_operation:
            return 'service_catalog.admin_request_on_service'
        if not self.operation.is_admin_operation:
            return 'service_catalog.request_on_service'

    def get_form_kwargs(self, step):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})

        if step == "1":
            kwargs.update({'service': self.service})
            kwargs.update({'operation': self.operation})
            # add data from step 0
            kwargs.update({'squest_instance_name': self.storage.data['step_data']['0']['0-squest_instance_name'][0]})
            scope_id = self.storage.data['step_data']['0']['0-quota_scope'][0]
            get_object_or_404(Scope, id=scope_id)
            kwargs.update({'quota_scope': scope_id})

        return kwargs

    def get_template_names(self):
        return "service_catalog/generic_form_multiple_step.html"

    def done(self, form_list, **kwargs):
        service_id = self.kwargs['service_id']
        operation_id = self.kwargs['operation_id']
        service = get_object_or_404(Service, **{'id': service_id, 'enabled': True})
        create_operation = get_object_or_404(Operation, id=operation_id)

        # get data from the first form
        squest_instance_name = form_list[0].cleaned_data["squest_instance_name"]
        quota_scope = form_list[0].cleaned_data["quota_scope"]

        # get data from the second form
        comment = form_list[1].cleaned_data["request_comment"]
        user_provided_survey_fields = dict()
        for field_key, value in form_list[1].cleaned_data.items():
            if field_key not in EXCLUDED_SURVEY_FIELDS:
                user_provided_survey_fields[field_key] = value

        # create the instance
        new_instance = Instance.objects.create(service=service, name=squest_instance_name, quota_scope=quota_scope,
                                               requester=self.request.user)
        # create the request
        new_request = Request.objects.create(instance=new_instance,
                                             operation=create_operation,
                                             fill_in_survey=user_provided_survey_fields,
                                             user=self.request.user)

        # save the comment
        message = None
        if comment is not None and comment != "":
            message = RequestMessage.objects.create(request=new_request, sender=self.request.user, content=comment)
        from service_catalog.mail_utils import send_mail_request_update
        send_mail_request_update(target_request=new_request, user_applied_state=new_request.user, message=message)

        return redirect('service_catalog:request_list')
