from Squest.utils.squest_form import SquestForm
from service_catalog.forms import FormGenerator


class ApproveWorkflowStepForm(SquestForm):

    def __init__(self, *args, **kwargs):
        self.target_request = kwargs.pop("target_request")
        self.user = kwargs.pop('user')
        super(ApproveWorkflowStepForm, self).__init__(*args, **kwargs)

        form_generator = FormGenerator(user=self.user, squest_request=self.target_request)
        self.fields.update(form_generator.generate_form())

    def save(self):
        user_provided_survey_fields = dict()
        readable_fields = self.target_request.approval_workflow_state.current_step.approval_step.readable_fields.all().values_list('variable', flat=True)
        for variable, value in self.cleaned_data.items():
            # keep only editable field
            if variable not in readable_fields:
                user_provided_survey_fields[variable] = value
        self.target_request.approval_workflow_state.approve_current_step(user=self.user, fill_in_survey=user_provided_survey_fields)
