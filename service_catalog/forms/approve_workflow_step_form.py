from Squest.utils.squest_form import SquestForm
from service_catalog.forms import FormGenerator


class ApproveWorkflowStepForm(SquestForm):

    def __init__(self, *args, **kwargs):
        self.target_request = kwargs.pop("target_request")
        self.user = kwargs.pop('user')
        super(ApproveWorkflowStepForm, self).__init__(*args, **kwargs)

        form_generator = FormGenerator(squest_request=self.target_request)
        self.fields.update(form_generator.generate_form())

    def save(self):
        user_provided_survey_fields = dict()
        for field_key, value in self.cleaned_data.items():
            # keep only editable field
            if field_key not in [tower_field.name for tower_field in self.target_request.approval_workflow_state.current_step.approval_step.readable_fields.all()]:
                user_provided_survey_fields[field_key] = value
        self.target_request.approval_workflow_state.approve_current_step(user=self.user, fill_in_survey=user_provided_survey_fields)
