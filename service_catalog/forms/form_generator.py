import logging

from service_catalog.models import ApprovalState, RequestState

logger = logging.getLogger(__name__)


class FormGenerator:

    def __init__(self, user, operation=None, squest_request=None, squest_instance=None, is_api_form=False,
                 quota_scope=None):
        self.user = user
        self.operation = operation
        self.squest_request = squest_request
        self.squest_instance = squest_instance
        self.is_api_form = is_api_form
        self.is_initial_form = False
        self.quota_scope = quota_scope
        if self.quota_scope is None:
            # try to get the quota scope from the instance
            if self.squest_request is not None:
                self.quota_scope = self.squest_request.instance.quota_scope
            elif self.squest_instance is not None:
                self.quota_scope = self.squest_instance.quota_scope
        if (self.operation and not self.squest_request and not self.squest_instance) or (
                self.operation and self.squest_instance):
            self.is_initial_form = True
        if self.operation is None:
            if self.squest_request:
                self.operation = self.squest_request.operation
        self.django_form = {}

    def generate_form(self):
        if self.operation is None or not self.operation.tower_survey_fields.exists():
            # empty survey, no fields to generate
            return self.django_form
        if self.is_initial_form:
            # get all field that are not disabled by the admin
            self._add_customer_field_only()
        elif self.squest_request and self.squest_request.approval_workflow_state:
            if self.squest_request.state == RequestState.ACCEPTED:
                self._add_all_fields()
            else:
                self._add_field_from_approval_step()
        else:
            self._add_all_fields()
        if self.squest_request:
            # this is an admin accept form
            self._prefill_form_with_customer_values()
        if self.squest_request and self.squest_request.approval_workflow_state:
            # this is an approval step accept form
            self._override_form_fields_with_previous_step_values()
        return self.django_form

    def _add_customer_field_only(self):
        for survey_field in self.operation.tower_survey_fields.filter(is_customer_field=True):
            self.django_form[survey_field.variable] = survey_field.get_field(
                quota_scope=self.quota_scope,
                instance=self.squest_instance,
                user=self.user,
                is_api=self.is_api_form
            )

    def _add_field_from_approval_step(self):
        # Readable fields
        for survey_field in self.squest_request.approval_workflow_state.current_step.approval_step.readable_fields.all():
            self.django_form[survey_field.variable] = survey_field.get_field(
                quota_scope=self.quota_scope,
                instance=self.squest_instance,
                user=self.user,
                is_api=self.is_api_form,
                disabled=True
            )
        # Writable fields
        for survey_field in self.squest_request.approval_workflow_state.current_step.approval_step.editable_fields.all():
            self.django_form[survey_field.variable] = survey_field.get_field(
                quota_scope=self.quota_scope,
                instance=self.squest_instance,
                user=self.user,
                is_api=self.is_api_form
            )

    def _add_all_fields(self):
        fields_to_add = self.operation.tower_survey_fields.exclude(variable__in=self.django_form.keys())
        for survey_field in fields_to_add:
            self.django_form[survey_field.variable] = survey_field.get_field(
                quota_scope=self.quota_scope,
                instance=self.squest_instance,
                user=self.user,
                is_api=self.is_api_form
            )

    def _prefill_form_with_customer_values(self):
        for field in self.django_form.keys():
            if field in self.squest_request.fill_in_survey:
                self.django_form.get(field).initial = self.squest_request.fill_in_survey[field]
                self.django_form.get(field).default = self.squest_request.fill_in_survey[field]
            if field in self.squest_request.admin_fill_in_survey:
                self.django_form.get(field).initial = self.squest_request.admin_fill_in_survey[field]
                self.django_form.get(field).default = self.squest_request.admin_fill_in_survey[field]

    def _override_form_fields_with_previous_step_values(self):
        for step in self.squest_request.approval_workflow_state.approval_step_states.filter(
                state=ApprovalState.APPROVED).order_by('approval_step__position'):
            for field, value in step.fill_in_survey.items():
                django_field = self.django_form.get(field)
                if django_field:
                    django_field.initial = value
                    django_field.default = value
