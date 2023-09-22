from rest_framework.serializers import Serializer

from service_catalog.forms import FormGenerator


class ApproveWorkflowStepSerializer(Serializer):

    def __init__(self, *args, **kwargs):
        self.target_request = kwargs.pop("target_request")
        self.user = kwargs.pop('user')
        super(ApproveWorkflowStepSerializer, self).__init__(*args, **kwargs)

        form_generator = FormGenerator(user=self.user, squest_request=self.target_request, is_api_form=True)
        self.fields.update(form_generator.generate_form())

    def save(self):
        user_provided_survey_fields = dict()
        editable_fields = self.target_request.approval_workflow_state.current_step.approval_step.editable_fields.values_list("variable", flat=True)
        for field_key, value in self.validated_data.items():
            # keep only editable field
            if field_key in editable_fields:
                user_provided_survey_fields[field_key] = value
        self.target_request.approval_workflow_state.approve_current_step(user=self.user,
                                                                         fill_in_survey=user_provided_survey_fields)
